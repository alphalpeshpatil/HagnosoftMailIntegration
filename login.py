import os
import pathlib

from flask import Flask, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

from Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']

app = Flask("Google Login App")
app.secret_key = "CodeSpecialist.com"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "900829648049-quo4shsm3pa4apj23t6hltih0p2t6tci.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper

def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    service =Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    emailMsg = 'You won rs 100,000'
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = 'alpeshpatilalpesh91@gmail.com'
    mimeMessage['subject'] = 'You won'
    mimeMessage.attach(MIMEText(emailMsg, 'plain'))
    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

    message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
    print(message)

    msg=service.users().messages().get(userId='me',id=message['id']).execute()
    print(msg['snippet'])

    return redirect(authorization_url)

@app.route("/")
def index():
    return "Hello World <a href='/login'><button>Login</button></a>"

if __name__ == "__main__":
    app.run(debug=True)