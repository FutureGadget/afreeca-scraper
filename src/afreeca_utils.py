from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from urllib.parse import urljoin
from urllib.parse import urlparse
from errors import NotOnAirException

from constants import *

def get_player(driver, broadcastUrl):
    try:
        driver.get(broadcastUrl)
        playButton = driver.find_element_by_xpath('//*[@id="bs-navi"]/div/article[1]/div[1]/a/span/img')
        WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="bs-navi"]/div/article[1]/div[1]/a/span/img')))
        thumbnailUrl = playButton.get_attribute('src') # returns None if not present. (e.g. Not on air.)
        o = urlparse(thumbnailUrl)
        webPlayerUrl = urljoin(urljoin(PLAYER_ROOT_URL, urlparse(broadcastUrl).path) + '/', o.path.split('/')[2].split('.')[0])
        print(f'live thumbnail: {o.path}')
        print(f'live web player url: {webPlayerUrl}')

        driver.get(webPlayerUrl)
        return driver
    except Exception as e:
        print(f'exception while getting afreeca player url for {broadcastUrl}, {e}')
        raise NotOnAirException()

if __name__ == '__main__':
    # broadcastUrl = SHINEE
    broadcastUrl = JIHO
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    # options.add_argument("disable-gpu")

    driver = webdriver.Chrome()

    driver = get_player(driver, JIHO)
    print(driver.current_url)
