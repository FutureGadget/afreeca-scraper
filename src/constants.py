from pathlib import Path

PLAYER_ROOT_URL = 'https://play.afreecatv.com/'

HORO = 'https://bj.afreecatv.com/scv6256'
SHINEE = 'https://bj.afreecatv.com/onlysibar'
JIHO = 'https://bj.afreecatv.com/jou1025'
PAGO = 'https://bj.afreecatv.com/rlatjdgus228'
DOJAE = 'https://bj.afreecatv.com/wodnrdldia'
HONG9 = 'https://bj.afreecatv.com/dpfgc3'
JUM = 'https://bj.afreecatv.com/jk890202'
JJUK = 'https://bj.afreecatv.com/tmsh401'

SCRIPT_PATH = Path(__file__).parent
VIDEO_DIR = (SCRIPT_PATH / '../videos').resolve()
TOKEN_DIR = (SCRIPT_PATH / '../token').resolve()
SECRETS_DIR = (SCRIPT_PATH / '../secrets').resolve()
LOG_DIR = (SCRIPT_PATH / '../logs').resolve()

#EMAIL_RECEPIENTS = ['danwoopark@gmail.com', 'whrwkd7@gmail.com']
EMAIL_RECEPIENTS = ['danwoopark@gmail.com']

if __name__ == '__main__':
    print(VIDEO_DIR)
    print(TOKEN_DIR)
    print(SECRETS_DIR)
