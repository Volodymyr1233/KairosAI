
from datetime import datetime,timezone
from typing import Optional
import google.auth.exceptions
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import json
#from Event import Event
from GoogleAPI.Event import Event
from googleapiclient.errors import HttpError




def getCredentials(user_token_dict:dict)->Credentials:
    """
       :param user_token_dict: data from .json file of token
       :return: Credentials object
       :raises google.auth.exceptions.RefreshError if cannot refresh token
    """
    creds = Credentials.from_authorized_user_info(user_token_dict)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except google.auth.exceptions.RefreshError as e:
                raise e
        else:
            raise google.oauth2.credentials.exceptions.DefaultCredentialsError('token is not valid')
    return creds

def getEvents(user_token_dict:dict,
              calendar_id: str = 'primary',
              time_min: str = datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat(),
              time_max: str = datetime(2100, 1, 1, tzinfo=timezone.utc).isoformat(),
              max_results: int = 15,
              order_by: str = 'startTime',
              show_deleted: bool = False,
              single_events: bool = True,
              show_hidden_invitations: bool = False,
              updated_min: Optional[datetime] = None,
              always_include_email: bool = True,
              )->list[Event] | HttpError:
    creds = getCredentials(user_token_dict)
    service = build('calendar', 'v3', credentials=creds)
    args = {
        'calendarId': calendar_id,
        'timeMin': time_min,
        'timeMax': time_max,
        'maxResults': max_results,
        'orderBy': order_by,
        'showDeleted': show_deleted,
        'singleEvents': single_events,
        'showHiddenInvitations': show_hidden_invitations,
        'updatedMin': updated_min,
        'alwaysIncludeEmail': always_include_email,
    }
    try:
        event_results = service.events().list(
            **args
        ).execute()
        return [Event(x) for x in event_results.get('items', [])]
    except HttpError as err:
        raise err

def addEvent(user_token_dict:dict,event: Event,calendar_id: str = 'primary',):
    service = build("calendar", "v3", credentials=getCredentials(user_token_dict))
    created_event = service.events().insert(calendarId=calendar_id, body=event.to_dict()).execute()
    return created_event

def updateEvent(user_token_dict:dict, event: Event, calendar_id: str = 'primary'):
    if not hasattr(event,'id') or event.id is None:
        raise ValueError('no eventId')
    service = build("calendar", "v3", credentials=getCredentials(user_token_dict))
    updated_event = service.events().update(calendarId=calendar_id,eventId=event.id, body=event.to_dict()).execute()
    return updated_event

if __name__ == '__main__':
    from Event import *
    secret_key_dict = None
    with open('googleapi_client_secret.json', 'r',encoding='UTF-8') as f:
        secret_key_dict = json.load(f)
    test_token = None
    with open('test_token.json', 'r',encoding='UTF-8') as f:
        test_token = json.load(f)
    def print_future_events():
        events = getEvents(test_token,time_min=datetime.now(timezone.utc).isoformat())
        for e in events:
            print(e)

    def add_event_test():
        e = (EventBuilder().
             with_summary('KairosAI_test idz na zajecia').with_description('test 03.06.25').
             with_start_date(datetime(2025,6,3,14,5,tzinfo=timezone.utc).isoformat()).
             with_end_date(datetime(2025,6,3,15,tzinfo=timezone.utc).isoformat()).
             with_reminders(useDefault=False,overrides=[{
            'method':"email","minutes":10
        }])
             ).build()
        print(e)
        x = addEvent(test_token,e)
        for k,v in x.items():
            print(k,v)
        x = EventBuilder(Event(x)).with_description('po updatecie').with_summary('kairosAU_update_test').build()
        x = updateEvent(test_token,x)
        for k,v in x.items():
            print(k,v)
    #add_event_test()
    print_future_events()



