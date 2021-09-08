from constants import TOKEN_DIR
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

import os

from constants import SECRETS_DIR

tokenFile = f'{TOKEN_DIR}/token.json'

client_secrets_file = f'{SECRETS_DIR}/client_secret_145861033977-k4oc4je2bmg8ai4undjd7190bebqm69i.apps.googleusercontent.com.json'

SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/drive']

def get_cred():
    creds = None
    # Get credentials and create an API client
    if os.path.exists(tokenFile):
        creds = Credentials.from_authorized_user_file(tokenFile, SCOPES)
    try:
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
                creds = flow.run_console()
            with open(tokenFile, 'w') as token:
                token.write(creds.to_json())
    except RefreshError as e:
        print(e)
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
        creds = flow.run_console()
        with open(tokenFile, 'w') as token:
            token.write(creds.to_json())
    except Exception as e:
        print(e)
    return creds
