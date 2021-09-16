from scraper import scrape
from constants import *

import os

if __name__ == '__main__':
    # Initialize directories
    mode = 0o666
    os.path.exists(TOKEN_DIR) or os.mkdir(TOKEN_DIR, mode)
    os.path.exists(SECRETS_DIR) or os.mkdir(SECRETS_DIR, mode)
    os.path.exists(VIDEO_DIR) or os.mkdir(VIDEO_DIR, mode)
    os.path.exists(LOG_DIR) or os.mkdir(LOG_DIR, mode)

    scrape(HORO)
