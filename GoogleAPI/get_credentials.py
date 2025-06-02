
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SECRET_KEY_PATH = "client_secret.json"
OUTPUT_KEY_PATH =  "test_token.json"
if __name__ == "__main__":
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_secrets_file(SECRET_KEY_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(OUTPUT_KEY_PATH, 'w',encoding='utf-8') as creds_file:
            creds_file.write(creds.to_json())
