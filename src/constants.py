"""
This module is to define constants
"""

from pathlib import Path
import configparser
import os

# Constants
PLAYER_ROOT_URL = "https://play.afreecatv.com/"

# Paths
SCRIPT_PATH = Path(__file__).parent
VIDEO_DIR = (SCRIPT_PATH / "../videos").resolve()
TOKEN_DIR = (SCRIPT_PATH / "../token").resolve()
SECRETS_DIR = (SCRIPT_PATH / "../secrets").resolve()
LOG_DIR = (SCRIPT_PATH / "../logs").resolve()
CONFIG_FILE_PATH = (SCRIPT_PATH / "../configs").resolve()
BANNER_FILE = (SCRIPT_PATH / "../banner.txt").resolve()

# Environment Postfixes
DEVELOP = "dev"
PRODUCTION = "prod"

# Read from config
config = configparser.ConfigParser()
CONFIG_FILE_NAME_PREFIX = "app_config"
CONFIG_FILE_EXTENSION = ".ini"
ENVIRONMENT = os.environ.get("ENV", DEVELOP)
config_file = (
    CONFIG_FILE_PATH / f"{CONFIG_FILE_NAME_PREFIX}-{ENVIRONMENT}{CONFIG_FILE_EXTENSION}"
)
config.read(config_file)

TARGET_BJ = config["Recording"]["target_bj_home_uri"]
EMAIL_RECIPIENTS = config["Notification"]["recipients"].split(",")
CLIENT_CRED_FILE = (SECRETS_DIR / config["Credential"]["file"]).resolve()
CHROME = config["Selenium"]["remote"]
WEBDRIVER_TYPE = config["Selenium"]["type"]
LOCATION = config["Selenium"]["location"]
SHOULD_UPLOAD = config.getboolean("Video", "upload")
MAX_SINGLE_FILE_SIZE = config.getint("Video", "max_single_file_size")
SHOULD_NOTIFY = config.getboolean("Notification", "notify")

if __name__ == "__main__":
    print(VIDEO_DIR)
    print(TOKEN_DIR)
    print(SECRETS_DIR)
    print(TARGET_BJ)
    print(CONFIG_FILE_PATH)
    print(EMAIL_RECIPIENTS)
    print(SHOULD_UPLOAD)
    print(config_file)
    print(CLIENT_CRED_FILE)
    print(CHROME)
    print(WEBDRIVER_TYPE)
    print(LOCATION)
    print(SHOULD_NOTIFY)
