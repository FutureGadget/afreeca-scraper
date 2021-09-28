from datetime import datetime
import os
import time

from constants import TOKEN_DIR, VIDEO_DIR

def get_date_time_file_name():
    now = datetime.now()
    return f'{now.strftime("%m-%d-%Y_%H-%M")}.mpeg'

def get_files_in_dir(dir_path: str):
    return [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

def get_file_paths_in_dir(dir_path: str):
    return [os.path.join(dir_path, f) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

def get_old_files(dir_path: str, days_after_modification: int):
    return [f for f in get_file_paths_in_dir(dir_path) if int((time.time() - os.path.getmtime(f)) / (60 * 60 * 24)) >= days_after_modification ]

if __name__ == '__main__':
    print(get_files_in_dir(VIDEO_DIR))
    print(get_file_paths_in_dir(VIDEO_DIR))
    print(get_old_files(TOKEN_DIR, 1))
