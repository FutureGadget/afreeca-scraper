from constants import LOG_DIR
import logging
from logging.handlers import RotatingFileHandler

# Logger Configs
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(thread)d %(levelname)s %(name)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', handlers=[logging.StreamHandler()])
logger = logging.getLogger("scraper")
logger.addHandler(RotatingFileHandler(f'{LOG_DIR}/error.log', mode='a', maxBytes=1024*1024*100, backupCount=50)) # log file total size: 500 megabytes
stream_logger = logging.getLogger("stream")
stream_logger.addHandler(RotatingFileHandler(f'{LOG_DIR}/stream.log', mode='a', maxBytes=1024*1024*100, backupCount=50)) # log file total size: 500 megabytes
