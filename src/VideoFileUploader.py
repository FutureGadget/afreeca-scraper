from enum import Enum

import google_drive_api
from constants import VIDEO_DIR
from fileutils import get_date_time_file_name
from fileutils import get_new_videos


class VideoUploaderType(Enum):
    GOOGLE_DRIVE = 0
    YOUTUBE = 1


def get_video_file_uploader(type: VideoUploaderType):
    if type is VideoUploaderType.GOOGLE_DRIVE:
        return GoogleDriveUploader()
    elif type is VideoUploaderType.YOUTUBE:
        return YoutubeUploader()


class VideoFileUploader:
    def upload_new_videos(self, existing_videos: list, should_save: bool):
        print('================================')
        print('=========STOP RECORDING=========')
        print('================================')

        new_videos = get_new_videos(existing_videos)

        if len(new_videos) > 0:
            print('===========================')
            print('=========NEW VIDEOS========')
            print(','.join(new_videos))
            print('===========================')
        else:
            print('-------NO NEW VIDEOS-------')

        if should_save and len(new_videos) > 0:
            self.save(new_videos)
        else:
            print('==============SKIP SAVING VIDEO FILES================')
            print(f'New downloads: {len(new_videos)} without uploading.')
            print('=====================================================')

    def save(self, new_videos: list):
        pass


class GoogleDriveUploader(VideoFileUploader):
    def save(self, new_videos: list):
        for filename in new_videos:
            google_drive_api.savdAndBroadcastEmail(get_date_time_file_name(), f'{VIDEO_DIR}/{filename}')


class YoutubeUploader(VideoFileUploader):
    def save(self, new_videos: list):
        pass
