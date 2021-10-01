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
from urllib3.util.retry import Retry

import logger_config
from afreeca_utils import get_player
from bj_tracker import ShineeTracker
from constants import *
from errors import NotOnAirException
from timer import Timer
from fileutils import get_legal_filename_string
from id_generator import generate_id

HEADLESS = True
LIVE_STREAMING_LAG_THRESHOLD_SEC = 10
RETRY_COUNT_THRESHOLD = 5
# Should sleep with buffer to keep pace with streaming server (where network request latencey exists)
SEGMENT_DURATION_BUFFER = 0.1

global g_quit
g_quit = False


def get_headers(cookies):
    return {'Cookie': create_live_cookie_string(cookies), 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3', 'Connection': 'keep-alive',
            'Host': 'pc-web.stream.afreecatv.com', 'Origin': 'https://play.afreecatv.com',
            'Referer': 'https://play.afreecatv.com/onlysibar/235673275', 'Sec-Fetch-Dest': 'emtpy',
            'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-site', 'TE': 'trailers',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'}


def create_live_cookie_string(cookie):
    return '; '.join(list(map(lambda c: str(c['name']) + '=' + str(c['value']), cookie)))


def scrape(bj_home_uri):
    driver = get_driver()
    try:
        print('=====================START====================')
        print('Start recording when the broadcasting is onair.')
        print('===============================================')
        do_scrape(driver, bj_home_uri)
    except NotOnAirException as e:
        print('!-------------------------------NOT ON AIR------------------------------!')
        print(" Start from the first since the broadcasting does not seem to be on air.")
        print('!-----------------------------------------------------------------------!')
    except Exception as e:
        logger_config.logger.error('!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        logger_config.logger.error('Exception while scraping...')
        logger_config.logger.error(traceback.format_exc())
        logger_config.logger.error('!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        raise e
    finally:
        driver.quit()


def get_driver() -> WebDriver:
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
    options.add_argument(
        "--no-sandbox")  # https://stackoverflow.com/questions/53902507/unknown-error-session-deleted-because-of-page-crash-from-unknown-error-cannot
    options.add_argument(
        "--disable-dev-shm-usage")  # https://stackoverflow.com/questions/53902507/unknown-error-session-deleted-because-of-page-crash-from-unknown-error-cannot
    options.add_argument("--window-size=1920,1080")

    return webdriver.Remote(command_executor='http://chrome:4444/wd/hub', desired_capabilities=caps,
                            options=options)  # connect remote webdriver to docker standalone chrome
    # return webdriver.Chrome(desired_capabilities=caps, options=options)


def do_scrape(driver: WebDriver, bj_home_uri: str):
    driver = get_player(driver, bj_home_uri)
    cookies = driver.get_cookies()
    print("*******COOKIES*******")
    print(cookies)
    print("*********************")

    broadcast_title = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="player_area"]/div[2]/div[2]/div[4]/span'))).text
    filename_friendly_broadcast_title = get_legal_filename_string(broadcast_title)

    filename = f"{VIDEO_DIR}/{filename_friendly_broadcast_title}-{generate_id(6)}.mpeg"
    logger_config.stream_logger.info(f'Save file name: {filename}')

    # Must click play button to start streaming.
    play = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="stop_screen"]/dl/dd[2]/a')))
    play.click()

    # Close the program install recommendation window.
    skip_to_low_quality_video = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="layer_high_quality"]/div/span/a')))
    skip_to_low_quality_video.click()
    scrape_with_retry(driver, filename, cookies)


def scrape_with_retry(driver: WebDriver, filename: str, cookies: dict):
    retrycnt = 0
    timer = Timer.threshold(LIVE_STREAMING_LAG_THRESHOLD_SEC)
    timer.start()
    while retrycnt < RETRY_COUNT_THRESHOLD:
        try:
            # download(driver, filename, cookies, timer)
            download_by_m3u8(driver, filename, cookies, timer)
            # retry
            print('Retrying...')
        except NotOnAirException as e:
            raise e
        except KeyboardInterrupt as e:
            print('Aborting by user request..')
            raise e
        except Exception as e:
            print('Exception while downloading...')
            print(traceback.format_exc())
        finally:
            timer.increase_threshold_and_reset()
            retrycnt += 1


def close_driver(driver):
    driver.close()


def download_by_m3u8(driver: WebDriver, filename: str, cookies: dict, timer: Timer):
    with cf.ThreadPoolExecutor(max_workers=5) as executor:
        finished = False
        m3u8Url = None
        try:
            while not finished:
                browser_log = driver.get_log('performance')
                events = [process_browser_log_entry(entry) for entry in browser_log]

                requests = [event for event in events if 'Network.request' in event['method']]

                if (len(requests)) == 0 and timer.is_over_due():
                    return

                for e in requests:
                    m3u8Req = find_m3u8_request(e)
                    if m3u8Req:
                        timer.reset()
                        m3u8Url = m3u8Req['request']['url']
                        finished = True
                        break

            executor.submit(close_driver, driver)

            if m3u8Url:
                print(f'Request m3u8 url detected: {m3u8Url}')
                ShineeTracker.broadcast_started()
                do_download(m3u8Url, filename, cookies, executor)

        except Exception as e:
            logger_config.logger.error('ERROR: Download by m3u8 exception: ')
            logger_config.logger.error(traceback.format_exc())


def enqueue_ts_urls(m3u8_url, cookies, _rq, q):
    unq = set()
    entries = queue.SimpleQueue()
    while not g_quit:
        sleep_time = 0
        try:
            res = _rq.get(m3u8_url, headers=get_headers(cookies), timeout=2)
            if res.status_code == 200:
                playlist = m3u8.loads(res.text)
                root_uri = get_m3u8_root_uri(m3u8_url)
                for s in playlist.segments:
                    if s.uri in unq:
                        print(f'Duplicate URI: {s.uri}')
                    else:
                        if len(unq) > 10:
                            old_uri = entries.get()
                            unq.remove(old_uri)
                        unq.add(s.uri)
                        entries.put(s.uri)
                        url = urljoin(root_uri, s.uri)
                        q.put((url, s.duration))
                        print(f'Put segment: url-{url}, duration-{s.duration} => OK')
                    sleep_time = sleep_time + s.duration - SEGMENT_DURATION_BUFFER
                print(f"m3u8 worker: Sleep {sleep_time} seconds.")
                time.sleep(sleep_time)
            else:
                logger_config.logger.error(
                    f"Received unexpected status code when requesting m3u8: {res.status_code, res.json}")
        except Exception as e:
            print('Error: Failed to get m3u8.')
            print(traceback.format_exc())
            raise NotOnAirException()


def do_download(m3u8_url: str, filename: str, cookies, executor: cf.ThreadPoolExecutor):
    s = rq.Session()
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[500, 502, 503, 504])
    s.mount('https://', HTTPAdapter(max_retries=retries))
    q = queue.Queue()

    # Thread(target=enqueue_ts_urls, args=(m3u8_url, cookies, s, q), daemon=True).start()
    futures = []
    futures.append(executor.submit(enqueue_ts_urls, m3u8_url, cookies, s, q))
    futures.append(executor.submit(download_segments, filename, q, s, cookies))

    # Keep looping to handle KeyboardInterrupt signal (SIGINT)
    # http://www.luke.maurits.id.au/blog/post/threads-and-signals-in-python.html
    # https://stackoverflow.com/questions/29177490/how-do-you-kill-futures-once-they-have-started
    try:
        while not all([future.done() for future in futures]):
            time.sleep(1)
    except KeyboardInterrupt as e:
        global g_quit
        g_quit = True
        raise e

    for future in cf.as_completed(futures):
        e = future.exception()
        if e:
            logger_config.logger.error(repr(e))
            raise e


def download_segments(filename: str, q: queue.Queue, _rq, cookies):
    with open(filename, 'ab') as file:
        while not g_quit:
            try:
                (url, duration) = q.get(timeout=30)
                r1 = _rq.get(url, stream=True, headers=get_headers(cookies), timeout=2)
                if r1.status_code == 200:
                    logger_config.stream_logger.debug(f'{url} => OK')
                    for chunk in r1.iter_content(chunk_size=1024):
                        file.write(chunk)
                    print(f'DOWNLOAD: {url} => OK')
                else:
                    logger_config.logger.error(
                        f"Received unexpected status code: {r1.status_code, r1.json} for segment: {url}")
                time.sleep(duration - SEGMENT_DURATION_BUFFER)
            except Exception as e:
                logger_config.logger.error('ERROR: Downloading segments from m3u8 playlist')
                logger_config.logger.error(traceback.format_exc())

                if not q.empty():
                    logger_config.logger.info('Try recover from error since the streaming queue is not empty.')
                    # Flush all delayed segments.
                    while not q.empty():
                        q.get(block=False)
                    pass
                else:
                    logger_config.logger.info('Stop downloading segments since the streaming has been stopped.')
                    raise NotOnAirException()
            finally:
                q.task_done()


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


def download(driver, filename, cookies, timer):
    # Keep downloading HLS streaming segments.
    while True:
        browser_log = driver.get_log('performance')
        events = [process_browser_log_entry(entry) for entry in browser_log]

        requests = [event for event in events if 'Network.request' in event['method']]
        # response = [event for event in events if 'Network.response' in event['method']]

        if len(requests) == 0 and timer.is_over_due():
            click_play_btn(driver, 10)
            click_play_btn(driver, 10)
            return

        for e in requests:
            tsReq = find_ts_request(e)
            if tsReq:
                timer.reset()
                url = tsReq['request']['url']
                r1 = rq.get(url, stream=True, headers=get_headers(cookies), timeout=2)
                if r1.status_code == 200:
                    print(f'{url} - OK')
                    with open(filename, 'ab') as f:
                        for chunk in r1.iter_content(chunk_size=1024):
                            f.write(chunk)
                else:
                    print(f"Received unexpected status code {r1.status_code, r1.json}")


def find_ts_request(e):
    if 'request' in e['params'].keys():
        if e['params']['request']['url'].endswith('.TS'):
            return e['params']


def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response
