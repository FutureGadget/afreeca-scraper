from pathlib import Path
import configparser

# Constants
PLAYER_ROOT_URL = 'https://play.afreecatv.com/'

# Paths
SCRIPT_PATH = Path(__file__).parent
VIDEO_DIR = (SCRIPT_PATH / '../videos').resolve()
TOKEN_DIR = (SCRIPT_PATH / '../token').resolve()
SECRETS_DIR = (SCRIPT_PATH / '../secrets').resolve()
LOG_DIR = (SCRIPT_PATH / '../logs').resolve()
CONFIG_FILE_PATH = (SCRIPT_PATH / '../app_config.ini').resolve()

# Read from config
config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)

TARGET_BJ = config['Recording']['target_bj_home_uri']
EMAIL_RECEPIENTS = config['Notification']['recipients'].split(',')

if __name__ == '__main__':
    print(VIDEO_DIR)
    print(TOKEN_DIR)
    print(SECRETS_DIR)
    print(CONFIG_FILE_PATH)
