import os
from pathlib import Path

PLAYER_ROOT_URL = 'https://play.afreecatv.com/'

HORO = 'https://bj.afreecatv.com/scv6256'
SHINEE = 'https://bj.afreecatv.com/onlysibar'
JIHO = 'https://bj.afreecatv.com/jou1025'

SCRIPT_PATH = Path(__file__).parent
VIDEO_DIR = (SCRIPT_PATH / '../videos').resolve()
TOKEN_DIR = (SCRIPT_PATH / '../token').resolve()
SECRETS_DIR = (SCRIPT_PATH / './secrets').resolve()

EMAIL_RECEPIENTS = ['danwoopark@gmail.com', 'whrwkd7@gmail.com']
SENDER = 'danwoopark@gmail.com'

if __name__ == '__main__':
    print(VIDEO_DIR)
    print(TOKEN_DIR)
    print(SECRETS_DIR)
