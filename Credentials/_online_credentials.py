
from oauthlib.oauth2.rfc6749.errors import AccessDeniedError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
SECRET_KEY_PATH = "E:\Programowanie\Python\KairosAI\Credentials\_local_resources\googleapi_client_secret.json"

def get_credentials()->Credentials | None:
    try:
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        flow = InstalledAppFlow.from_client_secrets_file(SECRET_KEY_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
        return creds
    except AccessDeniedError:
        return None


