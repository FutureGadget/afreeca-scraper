import concurrent.futures as cf
import json
import queue
import time
import traceback
from urllib.parse import urljoin
from urllib.parse import urlsplit

import m3u8
import requests as rq
from requests.adapters import HTTPAdapter
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from urllib3.util.retry import Retry

import logger_config
from afreeca_utils import get_player
from constants import *
from errors import NotOnAirException
from fileutils import get_legal_filename_string
from id_generator import generate_id
from ordered_set import OrderedSet
from timer import Timer
from bj_tracker import ShineeTracker

HEADLESS = True
LIVE_STREAMING_LAG_THRESHOLD_SEC = 10
RETRY_COUNT_THRESHOLD = 5
# Should sleep with buffer to keep pace with streaming server (where network request latencey exists)
SEGMENT_DURATION_BUFFER = 0.1

global G_QUIT
G_QUIT = False


def get_headers(cookies, uri):
    return {'Cookie': create_live_cookie_string(cookies), 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3', 'Connection': 'keep-alive',
            'Host': 'pc-web.stream.afreecatv.com', 'Origin': 'https://play.afreecatv.com', 'Referer': uri,
            'Sec-Fetch-Dest': 'emtpy', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-site', 'TE': 'trailers',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'}


def create_live_cookie_string(cookie):
    return '; '.join(list(map(lambda c: str(c['name']) + '=' + str(c['value']), cookie)))


def scrape(bj_home_uri, shinee_tracker):
    """
    Scrape if the broadcast started
    """
    try:
        driver = get_driver(WEBDRIVER_TYPE)
        print('=====================START====================')
        print('Start recording when the broadcasting is onair.')
        print('===============================================')
        do_scrape(driver, bj_home_uri, shinee_tracker)
    except NotOnAirException:
        print('!-------------------------------NOT ON AIR------------------------------!')
        print(" Start from the first since the broadcasting does not seem to be on air.")
        print('!-----------------------------------------------------------------------!')
    except Exception as exe:
        logger_config.logger.error('!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        logger_config.logger.error('Exception while scraping...')
        logger_config.logger.error(traceback.format_exc())
        logger_config.logger.error('!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        raise exe
    finally:
        driver.quit()


def get_driver(driver_type) -> WebDriver:
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
    options.add_argument(
        "--no-sandbox")  # https://stackoverflow.com/questions/53902507/unknown-error-session-deleted-because-of-page-crash-from-unknown-error-cannot
    options.add_argument("--single-process")
    options.add_argument(
        "--disable-dev-shm-usage")  # https://stackoverflow.com/questions/53902507/unknown-error-session-deleted-because-of-page-crash-from-unknown-error-cannot
    options.add_argument("--window-size=1024,768")

    if driver_type == 'REMOTE':
        return webdriver.Remote(command_executor=CHROME, desired_capabilities=caps, options=options)  # connect remote webdriver to docker standalone chrome
    else:
        # options.binary_location = '/usr/bin/google-chrome' # you have to install google-chrome binary
        return webdriver.Chrome(LOCATION, desired_capabilities=caps, options=options)


def do_scrape(driver: WebDriver, bj_home_uri: str, shinee_tracker: ShineeTracker):
    """
    Scrape and save the stream to the local filesystem while on-air
    """
    driver = get_player(driver, bj_home_uri)

    shinee_tracker.broadcast_started()

    cookies = driver.get_cookies()
    print("*******COOKIES*******")
    print(cookies)
    print("*********************")
    headers = get_headers(cookies, driver.current_url)
    print("*******HEADERS*******")
    print(headers)
    print("*********************")
    print(driver.current_url)

    broadcast_title = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="player_area"]/div[2]/div[2]/div[4]/span'))).text
    filename_friendly_broadcast_title = get_legal_filename_string(broadcast_title)

    filename = f"{VIDEO_DIR}/{filename_friendly_broadcast_title}-{generate_id(6)}.mpeg"
    logger_config.stream_logger.info('Save file name: %s', filename)

    # Close the program install recommendation window.
    try:
        skip_to_low_quality_video = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="layer_high_quality"]/div/span/a')))
        skip_to_low_quality_video.click()
    except TimeoutException:
        pass
    
    scrape_with_retry(driver, filename, headers)


def scrape_with_retry(driver: WebDriver, filename: str, headers):
    retrycnt = 0
    timer = Timer.threshold(LIVE_STREAMING_LAG_THRESHOLD_SEC)
    timer.start()
    while retrycnt < RETRY_COUNT_THRESHOLD:
        try:
            download_by_m3u8(driver, filename, headers, timer)
            print('Retrying...')
        except NotOnAirException as exe:
            raise exe
        except KeyboardInterrupt as exe:
            print('Aborting by user request..')
            raise exe
        except Exception as exe:
            print('Exception while downloading...')
            print(traceback.format_exc())
        finally:
            timer.increase_threshold_and_reset()
            retrycnt += 1


def close_driver(driver):
    driver.quit()


def download_by_m3u8(driver: WebDriver, filename: str, headers, timer: Timer):
    with cf.ThreadPoolExecutor(max_workers=5) as executor:
        finished = False
        m3u8_url = None
        try:
            while not finished:
                browser_log = driver.get_log('performance')
                events = [process_browser_log_entry(entry) for entry in browser_log]

                requests = [event for event in events if 'Network.request' in event['method']]

                if (len(requests)) == 0 and timer.is_over_due():
                    return

                for elem in requests:
                    m3u8_req = find_m3u8_request(elem)
                    if m3u8_req:
                        timer.reset()
                        m3u8_url = m3u8_req['request']['url']
                        finished = True
                        break

            executor.submit(close_driver, driver)

            if m3u8_url:
                print(f'Request m3u8 url detected: {m3u8_url}')
                do_download(m3u8_url, filename, headers, executor)

        except Exception:
            logger_config.logger.error('ERROR: Download by m3u8 exception: ')
            logger_config.logger.error(traceback.format_exc())


def enqueue_ts_urls(m3u8_url, headers, _rq, stream_queue):
    """
    Enqueue segment urls downloaded from playlist(m3u8) url to stream_queue while g_quit is false.
    The queue will be consumed and stream segments will be saved to a file.
    """
    uri_set_windowed = OrderedSet(window=1000)
    while not G_QUIT:
        sleep_time = 0
        try:
            res = _rq.get(m3u8_url, headers=headers, timeout=2)
            if res.status_code == 200:
                playlist = m3u8.loads(res.text)
                root_uri = get_m3u8_root_uri(m3u8_url)
                for seg in playlist.segments:
                    if seg.uri in uri_set_windowed:
                        print(f'Duplicate URI: {seg.uri}')
                    else:
                        uri_set_windowed.add(seg.uri)
                        url = urljoin(root_uri, seg.uri)
                        stream_queue.put((url, seg.duration))
                        print(f'Put segment: url-{url}, duration-{seg.duration} => OK')
                    sleep_time = sleep_time + seg.duration - SEGMENT_DURATION_BUFFER
                print(f"m3u8 worker: Sleep {sleep_time} seconds.")
                time.sleep(sleep_time)
            else:
                logger_config.logger.error(
                    "Received unexpected status code when requesting m3u8: {%s, %s}", 
                    res.status_code, res.json())
        except Exception as exc:
            print('Error: Failed to get m3u8.')
            print(traceback.format_exc())
            raise NotOnAirException() from exc


def do_download(m3u8_url: str, filename: str, headers, executor: cf.ThreadPoolExecutor):
    """
    Start 2 tasks.
    1. Enqueue segment(ts) urls from playlist url.
    2. Dequeue segment(ts) urls and download it.
    """
    session = rq.Session()
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    stream_queue = queue.Queue()

    futures = [executor.submit(enqueue_ts_urls, m3u8_url, headers, session, stream_queue),
               executor.submit(download_segments, filename, stream_queue, session, headers)]

    # Keep looping to handle KeyboardInterrupt signal (SIGINT)
    # http://www.luke.maurits.id.au/blog/post/threads-and-signals-in-python.html
    # https://stackoverflow.com/questions/29177490/how-do-you-kill-futures-once-they-have-started
    try:
        while not all(future.done() for future in futures):
            time.sleep(1)
    except KeyboardInterrupt as exe:
        global G_QUIT
        G_QUIT = True
        raise exe

    for future in cf.as_completed(futures):
        exe = future.exception()
        if exe:
            logger_config.logger.error(repr(exe))
            raise exe


def download_segments(filename: str, stream_queue: queue.Queue, _rq, headers):
    """
    Consume the streaming segments queue and download it while G_QUIT is false.
    """
    with open(filename, 'ab') as file:
        while not G_QUIT:
            try:
                (url, duration) = stream_queue.get(timeout=30)
                response = _rq.get(url, stream=True, headers=headers, timeout=2)
                if response.status_code == 200:
                    logger_config.stream_logger.debug('{%s} => OK', url)
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                    print(f'DOWNLOAD: {url} => OK')
                else:
                    logger_config.logger.error(
                        "Received unexpected status code: {%s, %s} for segment: {%s}", 
                        response.status_code, response.json, url)
                time.sleep(duration - SEGMENT_DURATION_BUFFER)
            except Exception as exe:
                logger_config.logger.error('ERROR: Downloading segments from m3u8 playlist')
                logger_config.logger.error(traceback.format_exc())

                if not stream_queue.empty():
                    logger_config.logger.info(
                        'Try recover from error since the streaming queue is not empty.')
                    # Flush all delayed segments.
                    while not stream_queue.empty():
                        uri = stream_queue.get(block=False)
                        logger_config.logger.info('Flushing delayed uris: {%s}', uri)
                else:
                    logger_config.logger.info(
                        'Stop downloading segments since the streaming has been stopped.')
                    raise NotOnAirException() from exe
            finally:
                stream_queue.task_done()


def get_m3u8_root_uri(m3u8_url):
    (scheme, netloc, path, _, _) = urlsplit(m3u8_url)
    return f'{scheme}://{netloc}/{path.split("/")[1]}/'  # must be trailing slash to be used in urljoin


def find_m3u8_request(e):
    if 'request' in e['params'].keys():
        if 'auth_playlist.m3u8' in e['params']['request']['url']:
            return e['params']


def click_play_btn(driver, wait_sec):
    WebDriverWait(driver, wait_sec).until(EC.element_to_be_clickable((By.ID, 'play')))
    playBtn = driver.find_element_by_id('play')
    action = ActionChains(driver)
    action.move_to_element_with_offset(playBtn, 2, 2)
    action.click()
    action.perform()


def find_ts_request(e):
    if 'request' in e['params'].keys():
        if e['params']['request']['url'].endswith('.TS'):
            return e['params']


def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response
