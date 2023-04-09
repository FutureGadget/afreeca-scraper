"""
This module enables a Google oauth2 login by exposing login endpoint
"""
import os
import json
from flask import Flask, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from constants import TOKEN_DIR

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")

google_blueprint = make_google_blueprint(
    client_id="215468960334-fvc1nev290ahh84a5hbti00nkah6rtgv.apps.googleusercontent.com",
    client_secret="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",
    scope=["openid", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/youtube.upload"],
    offline=True,
    redirect_url = "http://localhost:5000"
)
app.register_blueprint(google_blueprint, url_prefix="/login")

@app.route("/")
def index():
    """
    Login Google using OAuth2
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
