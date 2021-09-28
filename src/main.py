from scraper import scrape
from constants import *
from bannerprinter import show_banner
from bj_tracker import ShineeTracker
from video_file_uploader import save_and_upload_new_videos
import video_file_cleaner
import fileutils

import sys
import time
import os


if __name__ == '__main__':
    show_banner()
    print(f'Target BJ URI: {TARGET_BJ}')
    print(f'Email recipients: {EMAIL_RECEPIENTS}')

    shinee_tracker = ShineeTracker(start_tomorrow=True)
    
    while True:
        video_file_cleaner.clean_old_videos(days_after_modification = 3)
        existingVideos = fileutils.get_files_in_dir(VIDEO_DIR)
        print(f"Existing videos: {','.join(existingVideos)}")

        try:
            scrape(TARGET_BJ)
        except KeyboardInterrupt as e:
            print('=======SHUTDOWN REQUESTED======')
            print("Shutdown requested...existing.")
            print('===============================')
            break
        finally:
            save_and_upload_new_videos(existingVideos, SAVE_ON_DRIVE_AND_NOTIFY)
            shinee_tracker.send_email_if_had_no_live_today()
        time.sleep(60)

    sys.exit(0)
