import os

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from constants import CLIENT_CRED_FILE
from constants import TOKEN_DIR

import logger_config

SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/youtube']


def get_token_file() -> str:
    return f'{TOKEN_DIR}/token.json'


def get_cred():
    cred = None
    token_file = get_token_file()
    # Get credentials and create an API client
    if os.path.exists(token_file):
        cred = Credentials.from_authorized_user_file(token_file, SCOPES)
    try:
        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_CRED_FILE, SCOPES)
                cred = flow.run_console()
            with open(token_file, 'w') as token:
                token.write(cred.to_json())
    except RefreshError as e:
        logger_config.logger.exception('refresh error')
        return None
    except Exception as e:
        logger_config.logger.exception('unknown error while refreshing')
        return None
    return cred

