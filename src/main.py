import asyncio
import sys

import fileutils
import video_file_cleaner
from video_file_uploader import get_video_file_uploader
from bannerprinter import show_banner
from bj_tracker import ShineeTracker
from constants import *
from scraper import scrape

import logger_config


async def main():
    """
    This is the main entry point for the program
    """
    show_banner()
    print(f"Target BJ URI: {TARGET_BJ}")
    print(f"Email recipients: {EMAIL_RECIPIENTS}")

    shinee_tracker = ShineeTracker(start_tomorrow=True)
    youtube_uploader = await get_video_file_uploader()

    while True:
        video_file_cleaner.clean_old_videos(hours_after_modification=8)

        try:
            await scrape(TARGET_BJ, shinee_tracker, youtube_uploader)
        except KeyboardInterrupt:
            print("=======SHUTDOWN REQUESTED======")
            print("Shutdown requested...existing.")
            print("===============================")
            break
        except Exception:
            logger_config.logger.error("Ignoring Unknown Error")
        finally:
            files_to_upload = fileutils.get_file_paths_in_dir(VIDEO_DIR)
            if len(files_to_upload) > 0:
                await youtube_uploader.upload_and_delete_file_async(files_to_upload[0])
            shinee_tracker.send_email_if_had_no_live_today()
        await asyncio.sleep(60)

    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
