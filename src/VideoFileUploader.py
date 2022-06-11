import youtube_api
from constants import VIDEO_DIR
from fileutils import get_new_videos
from gmail import broadcast_to_enrolled_users
from google_cred import get_cred

import logger_config

def get_video_file_uploader():
    get_cred()  # initialize token
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
            file_links = self.save(new_videos)
            for (filename, link) in file_links:
                broadcast_to_enrolled_users(f'[Live Recording]{filename}', f'링크: {link}')
        else:
            print('==============SKIP SAVING VIDEO FILES================')
            print(f'New downloads: {len(new_videos)} without uploading.')
            print('=====================================================')

    def save(self, new_videos: list) -> list:
        pass


class YoutubeUploader(VideoFileUploader):
    def save(self, new_videos: list):
        filename_and_links = []
        for filename in new_videos:
            saved = youtube_api.save(filename, f'{VIDEO_DIR}/{filename}')
            if saved is not None:
                filename_and_links.append((filename, saved))
            else:
                logger_config.logger.error('Skipping Youtube upload: ' + filename)
        return filename_and_links


if __name__ == '__main__':
    ytube_uploader = get_video_file_uploader()
    ytube_uploader.upload_new_videos([], True)
