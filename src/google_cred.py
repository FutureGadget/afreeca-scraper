import os

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import google_auth_oauthlib.flow

from constants import CLIENT_CRED_FILE
from constants import TOKEN_DIR

import logger_config

SCOPES = ['https://www.googleapis.com/auth/gmail.send','https://www.googleapis.com/auth/youtube.upload']


def get_token_file() -> str:
    return f'{TOKEN_DIR}/token.json'
