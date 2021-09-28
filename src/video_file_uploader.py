import os

import google_drive_api
from constants import VIDEO_DIR
from fileutils import get_date_time_file_name
from fileutils import get_files_in_dir

def save_and_upload_new_videos(existingVideos, save_google_drive):
    print('================================')
    print('=========STOP RECORDING=========')
    print('================================')
    newDownloads = get_new_videos(existingVideos)
    if len(newDownloads) > 0 and save_google_drive:
        save_all_and_broadcast_email(newDownloads)
    elif not save_google_drive:
        print('==============SKIP SAVING GOOGLE DRIVE================')
        print(f'New downloads: {len(newDownloads)} without uploading.')
        print('======================================================')

def save_all_and_broadcast_email(filenames):
    for filename in filenames:
        google_drive_api.savdAndBroadcastEmail(get_date_time_file_name(), f'{VIDEO_DIR}/{filename}')

def get_new_videos(existingVideos):
    newVideos = [ f for f in get_files_in_dir(VIDEO_DIR) if f not in existingVideos ]
    if len(newVideos) > 0:
        print('===========================')
        print('=========NEW VIDEOS========')
        print(','.join(newVideos))
        print('===========================')
    else:
        print('-------NO NEW VIDEOS-------')
    return newVideos
