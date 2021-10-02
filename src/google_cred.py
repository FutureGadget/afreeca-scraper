from constants import TOKEN_DIR
from constants import GOOGLE_DRIVE_CRED_FILE
from constants import YOUTUBE_CRED_FILE
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

import os

from constants import SECRETS_DIR
from video_uploader_type import VideoUploaderType

SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/youtube']


def get_token_file(video_uploader_type: VideoUploaderType) -> str:
    if video_uploader_type == VideoUploaderType.GOOGLE_DRIVE:
        return f'{TOKEN_DIR}/googledrive/token.json'
    elif video_uploader_type == VideoUploaderType.YOUTUBE:
        return f'{TOKEN_DIR}/youtube/token.json'


def get_client_secrets_file(video_uploader_type: VideoUploaderType) -> str:
    if video_uploader_type == VideoUploaderType.GOOGLE_DRIVE:
        return f'{SECRETS_DIR}/googledrive/{GOOGLE_DRIVE_CRED_FILE}'
    elif video_uploader_type == VideoUploaderType.YOUTUBE:
        return f'{SECRETS_DIR}/youtube/{YOUTUBE_CRED_FILE}'


def get_cred(video_uploader_type: VideoUploaderType = VideoUploaderType.GOOGLE_DRIVE):
    cred = None
    token_file = get_token_file(video_uploader_type)
    client_secrets_file = get_client_secrets_file(video_uploader_type)
    # Get credentials and create an API client
    if os.path.exists(token_file):
        cred = Credentials.from_authorized_user_file(token_file, SCOPES)
    try:
        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
                cred = flow.run_console()
            with open(token_file, 'w') as token:
                token.write(cred.to_json())
    except RefreshError as e:
        print(e)
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
        cred = flow.run_console()
        with open(token_file, 'w') as token:
            token.write(cred.to_json())
    except Exception as e:
        print(e)
    return cred
