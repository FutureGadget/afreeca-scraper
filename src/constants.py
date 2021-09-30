from pathlib import Path
import configparser
import os

# Constants
PLAYER_ROOT_URL = 'https://play.afreecatv.com/'

# Paths
SCRIPT_PATH = Path(__file__).parent
VIDEO_DIR = (SCRIPT_PATH / '../videos').resolve()
TOKEN_DIR = (SCRIPT_PATH / '../token').resolve()
SECRETS_DIR = (SCRIPT_PATH / '../secrets').resolve()
LOG_DIR = (SCRIPT_PATH / '../logs').resolve()
CONFIG_FILE_PATH = (SCRIPT_PATH / '../configs').resolve()
BANNER_FILE = (SCRIPT_PATH / '../banner.txt').resolve()

# Environment Postfixes
DEVELOP = 'dev'
PRODUCTION = 'prod'

# Read from config
config = configparser.ConfigParser()
CONFIG_FILE_NAME_PREFIX = 'app_config'
CONFIG_FILE_EXTENSION = '.ini'
ENVIRONMENT = os.environ.get('ENV', DEVELOP)
config_file = (CONFIG_FILE_PATH / f"{CONFIG_FILE_NAME_PREFIX}-{ENVIRONMENT}{CONFIG_FILE_EXTENSION}")
config.read(config_file)

TARGET_BJ = config['Recording']['target_bj_home_uri']
EMAIL_RECEPIENTS = config['Notification']['recipients'].split(',')
SAVE_ON_DRIVE_AND_NOTIFY = config.getboolean('Notification', 'save_on_google_drive_and_notify')
CREDENTIAL_FILE = config['Credential']['file']

if __name__ == '__main__':
    print(VIDEO_DIR)
    print(TOKEN_DIR)
    print(SECRETS_DIR)
    print(TARGET_BJ)
    print(CONFIG_FILE_PATH)
    print(EMAIL_RECEPIENTS)
    print(SAVE_ON_DRIVE_AND_NOTIFY)
    print(config_file)
    print(CREDENTIAL_FILE)
