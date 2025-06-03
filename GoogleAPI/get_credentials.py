from oauthlib.oauth2.rfc6749.errors import AccessDeniedError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials


SECRET_KEY_PATH = "E:/Programowanie/Python/KairosAI/GoogleAPI/googleapi_client_secret.json"

def get_credentials()->Credentials | None:
    try:
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        flow = InstalledAppFlow.from_client_secrets_file(SECRET_KEY_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
        return creds
    except AccessDeniedError:
        return None


if __name__ == "__main__":
        OUTPUT_KEY_PATH = "test_token.json"
        d = get_credentials()
        print(d.__class__.__name__)
        print(d)
        with open(OUTPUT_KEY_PATH, 'w') as f:
            f.write(d.to_json())
