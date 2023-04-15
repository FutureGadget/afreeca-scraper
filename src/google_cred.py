"""
Google credential management
"""
import asyncio
import json
from datetime import datetime, timedelta
import pytz
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from constants import TOKEN_DIR
from constants import CLIENT_CRED_FILE

import logger_config

SCOPES = ["openid",
          "https://www.googleapis.com/auth/userinfo.profile", 
          "https://www.googleapis.com/auth/userinfo.email", 
          "https://www.googleapis.com/auth/gmail.send", 
          "https://www.googleapis.com/auth/youtube.upload"]

def get_token_file() -> str:
    """
    Get Token file
    """
    return f'{TOKEN_DIR}/token.json'

def get_client_cred_file() -> str:
    """
    Get Client Credential file (The file can be downloaded from the Google Cloud Console)
    """
    return CLIENT_CRED_FILE

def refresh_buffer():
    """
    Returns token expiration buffer to trigger an early token refresh
    """
    return timedelta(minutes=5)

def get_authorized_user_info() -> dict:
    """
    Authorized User Info in Google format
    """
    with open(get_token_file(), 'r', encoding='utf-8') as token_file:
        with open(get_client_cred_file(), 'r', encoding='utf-8') as cred_file:
            token_data = json.load(token_file)
            cred_data = json.load(cred_file)['web']
            return {
                'token': token_data['access_token'],
                'refresh_token': token_data['refresh_token'],
                'scopes': SCOPES,
                'client_id': cred_data['client_id'],
                'client_secret': cred_data['client_secret'],
                'quota_project_id': cred_data['project_id'],
                'expiry': (datetime.utcfromtimestamp(token_data['expires_at']).replace(tzinfo=pytz.UTC) - refresh_buffer()).isoformat()
            }


async def get_cred() -> Credentials:
    """
    Get Google Credentials from token file
    """
    try:
        with open(get_token_file(), 'r', encoding='utf-8') as token_file:
            token_data = json.load(token_file)
            credentials = Credentials.from_authorized_user_info(info=get_authorized_user_info())
            if credentials.expired:
                await asyncio.to_thread(credentials.refresh, Request())
                token_data['access_token'] = credentials.token
                token_data['expires_in'] = (credentials.expiry - datetime.utcnow()).total_seconds()
                token_data['expires_at'] = credentials.expiry.replace(tzinfo=pytz.UTC).timestamp()
                with open(get_token_file(), 'w', encoding='utf-8') as new_token_file:
                    json.dump(token_data, new_token_file)
            return credentials
    except RefreshError as ex:
        logger_config.logger.error("error while get cred %s", ex, stack_info = True)

if __name__ == '__main__':
    pass
    # cred = get_cred() TODO: run it asynchronously
    # print('expiry', cred.expiry.replace(tzinfo=pytz.UTC).isoformat())
    # print('expiry', (cred.expiry.replace(tzinfo=pytz.UTC)).timestamp())
