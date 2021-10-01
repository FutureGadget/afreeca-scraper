from constants import VIDEO_DIR
import fileutils
import os


def clean_old_videos(days_after_modification: int):
    for old_file_path in fileutils.get_old_files(dir_path=VIDEO_DIR, days_after_modification=days_after_modification):
        os.remove(old_file_path)
