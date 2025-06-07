
from datetime import datetime,timezone,timedelta
from typing import Optional
import google.auth.exceptions
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
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
                raise google.auth.exceptions.RefreshError(f'cannot refresh token: {e}')
        else:
            raise google.oauth2.credentials.exceptions.DefaultCredentialsError('token is not valid')
    return creds

def getEvents(user_token_dict:dict,
              calendar_id: str = 'primary',
              time_min: str = datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat(),
              time_max: str = datetime(2100, 1, 1, tzinfo=timezone.utc).isoformat(),
              max_results: int = 200,
              order_by: str = 'startTime',
              show_deleted: bool = False,
              single_events: bool = True,
              show_hidden_invitations: bool = False,
              updated_min: Optional[datetime] = None,
              always_include_email: bool = True,
              query=''
              )->list[Event] | None:
    """:arguments description: https://developers.google.com/workspace/calendar/api/v3/reference/events/list?hl=pl"""
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
        'q':query
    }
    try:
        event_results = service.events().list(
            **args
        ).execute()
        return [Event(x) for x in event_results.get('items', [])]
    except HttpError:
        return None

def addEvent(user_token_dict:dict,event: Event,calendar_id: str = 'primary',)->Event | None:
    service = build("calendar", "v3", credentials=getCredentials(user_token_dict))
    try:
        created_event = service.events().insert(calendarId=calendar_id, body=event.to_dict()).execute()
    except HttpError:
        return None
    return Event(created_event)

def updateEvent(user_token_dict:dict, event: Event, calendar_id: str = 'primary')->Event | None:
    if not hasattr(event,'id') or event.id is None:
        raise ValueError('no eventId')
    service = build("calendar", "v3", credentials=getCredentials(user_token_dict))
    try:
        updated_event = service.events().update(calendarId=calendar_id,eventId=event.id, body=event.to_dict()).execute()
    except HttpError:
        return None
    return Event(updated_event)
def deleteEvent(user_token_dict:dict, event: Event, calendar_id: str = 'primary')->bool | None:
    if not hasattr(event,'id') or event.id is None:
        raise ValueError('no eventId')
    service = build("calendar", "v3", credentials=getCredentials(user_token_dict))
    try:
        service.events().delete(calendarId=calendar_id,eventId=event.id).execute()
    except HttpError:
        return False
    return True


class Reminder:
    """Reminder for one user, and his credential"""
    def __init__(self,user_token_dict:dict):
        self._user_token_dict = user_token_dict
        self._events = [] #sorted by date
        pass
    def setSetUserToken(self,user_token_dict:dict):
        self._user_token_dict = user_token_dict
    def isValidCredential(self):
        try:
            getCredentials(self._user_token_dict)
            return True
        except Exception:
            return False
    def update(self,time_max:str=None):
        """:param time_max: Proper format: 2026-07-01T15:31:00+00:00"""
        time_min = datetime.now().isoformat()
        events = getEvents(self._user_token_dict,time_min=time_min) if time_max is None else getEvents(self._user_token_dict,time_max=time_max)
        self._events = []

        def __inner_f(ev) -> datetime:
            max = 0
            for x in ev.reminders['overrides']:
                if x['minutes'] > max:
                    max = x['minutes']
            return datetime.fromisoformat(ev.start) - timedelta(minutes=max)

        for event in events:
            if  hasattr(event,'reminders') and 'overrides' in event.reminders:
                self._events.append((event,__inner_f(event)))
        self._events = sorted(self._events, key=lambda ev: ev[1])

    def get(self,now=datetime.now().isoformat())->list[Event]:
        result = []
        for event,time in self._events:
            if time <= now:
                result.append(event)
        return result
