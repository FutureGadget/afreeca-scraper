from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver import ActionChains
import json
import requests as rq

from afreeca_utils import get_player_url
import google_drive_api
from constants import *
from fileutils import get_date_time_file_name
from timer import Timer, TimerError

import time
import os
import sys

### Options
TARGET_BJ = HORO

HEADLESS = True
LIVE_STREAMING_LAG_THRESHOLD_SEC = 10
RETRY_COUNT_THRESHOLD = 10

def get_headers(cookies):
    return {'Cookie': create_live_cookie_string(cookies), 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3', 'Connection': 'keep-alive', 'Host': 'pc-web.stream.afreecatv.com', 'Origin': 'https://play.afreecatv.com', 'Referer': 'https://play.afreecatv.com/onlysibar/235673275','Sec-Fetch-Dest': 'emtpy', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-site', 'TE': 'trailers', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'}

def create_live_cookie_string(cookie):
    return '; '.join(list(map(lambda c: str(c['name']) + '=' + str(c['value']), cookie)))

def main():
    existingVideos = [f for f in os.listdir(VIDEO_DIR) if os.path.isfile(os.path.join(VIDEO_DIR, f))]
    print(f"Existing videos: {','.join(existingVideos)}")
    try:
        while True:
            driver = get_driver()
            try:
                print('방송이 시작되면 녹화.')
                do_scrape(driver, TARGET_BJ)
            except Exception as e:
                print(e)
            finally:
                newDownloads = get_new_videos(existingVideos)
                if len(newDownloads) > 0:
                    save_all(newDownloads)
                print('녹화를 종료.')
                driver.quit()
            time.sleep(60)
    except KeyboardInterrupt:
        print("Shutdown requested...existing.")
    sys.exit(0)

def save_all(filenames):
    for filename in filenames:
        google_drive_api.save(get_date_time_file_name(), f'{VIDEO_DIR}/{filename}')

def get_new_videos(existingVideos):
    newVideos = [ f for f in os.listdir(VIDEO_DIR) if os.path.isfile(os.path.join(VIDEO_DIR, f)) and f not in existingVideos ]
    print(f"New vidoes: {','.join(newVideos)}")
    return newVideos

def get_driver():
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument('headless')
        options.add_argument("disable-gpu")
    options.add_argument('--window-size=1920,1080')
    
    return webdriver.Chrome(desired_capabilities=caps, options=options)

def do_scrape(driver, broadcastUrl):
    driver.get(broadcastUrl)

    webPlayerUrl = get_player_url(driver, broadcastUrl)

    if not webPlayerUrl:
        print('현재 방송중이 아님')
    else:
        driver.get(webPlayerUrl)
        WebDriverWait(driver, 10).until(EC.new_window_is_opened)
        cookies = driver.get_cookies()
        print(cookies)

        filename = f"{VIDEO_DIR}/{str(int(time.time()))}.mpeg"
        # Must click play button to start streaming.
        play = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="stop_screen"]/dl/dd[2]/a')))
        play.click()

        # Close the program install recommendation window.
        # if not HEADLESS:
        skip_to_low_quality_video = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="layer_high_quality"]/div/span/a')))
        skip_to_low_quality_video.click()

        retrycnt = 0
        timer = Timer.threshold(LIVE_STREAMING_LAG_THRESHOLD_SEC)
        timer.start()
        while retrycnt < RETRY_COUNT_THRESHOLD:
            try:
                download(driver, filename, cookies, timer)
                click_play_btn(driver)
                click_play_btn(driver)
                # retry
                print('Retrying...')
            except KeyboardInterrupt as e:
                print('Aborting by user request..')
                break
            except Exception as e:
                print(e)
            finally:
                timer.increase_threshold_and_reset()
                retrycnt += 1



def click_play_btn(driver):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'play')))
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

if __name__ == '__main__':
    main()
