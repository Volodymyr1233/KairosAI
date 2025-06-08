from oauthlib.oauth2.rfc6749.errors import AccessDeniedError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import json
import google.auth.exceptions
from Credentials._local_resources import Models
from GoogleAPI import GoogleCalendarAPI
from pathlib import Path

SECRET_KEY_PATH = str(Path(__file__).resolve().parent/"googleapi_client_secret.json")

def get_credentials()->Credentials | None:
    try:
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        flow = InstalledAppFlow.from_client_secrets_file(SECRET_KEY_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
        return creds
    except AccessDeniedError:
        return None


def auth_into_db(user_id:str)->bool:
    creds = get_credentials()
    if creds is not None:
        d = {'id':user_id}
        d.update(json.loads(creds.to_json()))
        Models.user_google_token.insert(**d).on_conflict_replace().execute()
        return True
    else:
        return False

def get_credentials_from_db(user_id:str)->dict | None:
    get = Models.user_google_token.get_or_none(id=user_id)
    return get.__dict__['__data__'] if get is not None else None
def check_user_credentials_from_db(user_id:str)->bool:
    creds = get_credentials_from_db(user_id)
    if creds is None:
        return False
    try:
        GoogleCalendarAPI.getCredentials(creds)
        return True
    except google.auth.exceptions.GoogleAuthError:
        return False


if __name__ == "__main__":
        """
        jesli chcesz recznie token zrobic
        OUTPUT_KEY_PATH = "test_token.json"
        d = get_credentials()
        print(d.__class__.__name__)
        print(d)
        with open(OUTPUT_KEY_PATH, 'w') as f:
            f.write(d.to_json())
        """
        auth_into_db('5')
        cred = get_credentials_from_db('5')
        x = GoogleCalendarAPI.getEvents(cred)
        for e in x:
            print(e)
