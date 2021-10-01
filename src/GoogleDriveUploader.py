import google_drive_api
from VideoFileUploader import VideoFileUploader
from constants import VIDEO_DIR
from fileutils import get_date_time_file_name


class GoogleDriveUploader(VideoFileUploader):
    def save(self, new_videos: list):
        for filename in new_videos:
            google_drive_api.save(get_date_time_file_name(), f'{VIDEO_DIR}/{filename}')
