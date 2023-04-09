"""
This module is a Flask app module which enables users to login in with their Google account.
"""
import os
import json
from flask import Flask, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from constants import TOKEN_DIR, CLIENT_CRED_FILE
from google_cred import SCOPES

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")

def get_google_blueprint(google_cred_file):
    with open(google_cred_file, 'r', encoding='utf-8') as cred_file:
        creds = json.load(cred_file)['web']
        return make_google_blueprint(
            client_id=creds['client_id'],
            client_secret=creds['client_secret'],
            scope=SCOPES,
            offline=True,
            redirect_url = "http://localhost:5000"
        )

google_blueprint = get_google_blueprint(CLIENT_CRED_FILE)
app.register_blueprint(google_blueprint, url_prefix="/login")

@app.route("/")
def index():
    """
    Login Google using OAuth2
    http://localhost:5000/login/google/authorized, http://localhost:5000 
    must be included in the authorized redirection url list in google oauth2 client admin page
    (https://console.cloud.google.com/apis/credentials?project=afreecascraper)
    """
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v1/userinfo")
    if resp.ok:
        return f"Hello, {resp.json()}!"
    return "Could not fetch your information."

def save_token_to_file(sender, token):
    """
    Save token to the token.json file so that we can reuse it later such as when calling google apis.
    """
    with open(f"{TOKEN_DIR}/token.json", "w", encoding='utf-8') as token_file:
        json.dump(token, token_file)

oauth_authorized.connect_via(google_blueprint)(save_token_to_file)

if __name__ == "__main__":
    # os.environ["FLASK_ENV"] = "development"
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
    app.run(host='0.0.0.0')
