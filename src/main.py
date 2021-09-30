import sys
import time

import fileutils
import video_file_cleaner
from VideoFileUploader import VideoUploaderType
from VideoFileUploader import get_video_file_uploader
from bannerprinter import show_banner
from bj_tracker import ShineeTracker
from constants import *
from scraper import scrape

if __name__ == '__main__':
    show_banner()
    print(f'Target BJ URI: {TARGET_BJ}')
    print(f'Email recipients: {EMAIL_RECEPIENTS}')

    shinee_tracker = ShineeTracker(start_tomorrow=True)
    uploader = get_video_file_uploader(VideoUploaderType.GOOGLE_DRIVE)
    
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
            uploader.upload_new_videos(existingVideos, SAVE_ON_DRIVE_AND_NOTIFY)
            shinee_tracker.send_email_if_had_no_live_today()
        time.sleep(60)

    sys.exit(0)
