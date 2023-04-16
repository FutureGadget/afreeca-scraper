"""
A module that contains apis to upload video file on an external system such as Youtube.
"""
import os
import asyncio
import youtube_api
from constants import SHOULD_NOTIFY, SHOULD_UPLOAD
from gmail import broadcast_to_enrolled_users
from google_cred import get_cred

import logger_config

async def get_video_file_uploader():
    await get_cred()  # initialize token
    return YoutubeUploader()


class VideoFileUploader:
    """
    A class to upload video file and delete the file when upload finishes
    """
    async def upload_and_delete_file_async(self, abs_path):
        print("Start uploading asynchronously", abs_path)
        await self.do_upload_and_delete_file_on_finish(abs_path)

    async def do_upload_and_delete_file_on_finish(self, abs_path):
        print('================================')
        print('=========Uploading File=========')
        print('================================')

        if abs_path is None:
            print('-------No file to upload-------')
            return

        if SHOULD_UPLOAD:
            (filename, link) = await self.upload(abs_path)
            if link is not None:
                if SHOULD_NOTIFY:
                    await broadcast_to_enrolled_users(f'[Live Recording]{filename}', f'링크: {link}')
                os.remove(abs_path)

        else:
            print('==============SKIP SAVING VIDEO FILES================')
            print(f'New downloads: {abs_path} without uploading.')
            print('=====================================================')

    async def upload(self, abs_path):
        """
        Upload the file on abs_path
        """


class YoutubeUploader(VideoFileUploader):
    """
    Upload a video file to a private youtube channel
    """
    async def upload(self, abs_path):
        try:
            with open(abs_path, 'rb') as file:
                filename = os.path.basename(file.name)
                filename_without_ext = filename[:filename.rfind('.')]
                saved = await youtube_api.save(filename_without_ext, os.path.abspath(file.name))
                if saved is not None:
                    return (filename, saved)
                else:
                    logger_config.logger.error('Skipping Youtube upload: %s', filename)
        except Exception:
            logger_config.logger.error('Error while uploading file %s', abs_path)
        return (None, None)
