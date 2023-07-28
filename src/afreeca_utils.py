"""
This module defines utils for afreeca player
"""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from errors import NotOnAirException

PLAYER_BOX_XPATH = '//*[@id="bs-navi"]/div/article[2]/div/a'
WAIT_SEC = 3

def get_player(driver, bj_home_url):
    """
    Go to the bjHomeUrl and click the anchor element to go to the actual broadcast link.
    Raises exception when the BJ is not on air.
    """
    try:
        driver.get(bj_home_url)
        wait = WebDriverWait(driver, WAIT_SEC)
        current_window = driver.current_window_handle


        wait.until(EC.element_to_be_clickable((By.XPATH, PLAYER_BOX_XPATH))).click()

        # Wait until the broadcast window is opened and switch to the new window.
        wait.until(EC.new_window_is_opened)
        new_window = set(driver.window_handles) - set([current_window])
        driver.switch_to.window(new_window.pop())

        return driver
    except Exception as exc:
        raise NotOnAirException() from exc
