import json

import google.auth.exceptions

import Models
from GoogleAPI import get_credentials,GoogleCalendarAPI,Event
def auth_into_db(user_id:str)->bool:
    creds = get_credentials.get_credentials()
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
if __name__ == '__main__':
   if not check_user_credentials_from_db('5'):
       auth_into_db('5')
   from datetime import datetime,timezone
   for e in GoogleCalendarAPI.getEvents(get_credentials_from_db('5'),time_min=datetime(2025,6,3,tzinfo=timezone.utc).isoformat(),time_max=datetime(2025, 6, 6, tzinfo=timezone.utc).isoformat()):
       print(e)

