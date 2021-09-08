from constants import TOKEN_DIR
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

import os

tokenFile = f'{TOKEN_DIR}/token.json'

def get_cred(client_secrets_file, scopes):
    creds = None
    # Get credentials and create an API client
    if os.path.exists(tokenFile):
        creds = Credentials.from_authorized_user_file(tokenFile, scopes)
    try:
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
                creds = flow.run_console()
            with open(tokenFile, 'w') as token:
                token.write(creds.to_json())
    except RefreshError as e:
        print(e)
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
        creds = flow.run_console()
        with open(tokenFile, 'w') as token:
            token.write(creds.to_json())
    except Exception as e:
        print(e)
    return creds
