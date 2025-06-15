from datetime import datetime,timezone

class Event:
    def __init__(self, data=None):
        if data is None:
            data = {
                'summary':'',
                'start':{},
                'end':{}
            }
        for key, value in data.items():
            setattr(self, key, value)
    def __str__(self):
        r= ''
        for k,e in self.__dict__.items():
            r+=f'{k}: {e}\n'
        return r
    def to_dict(self):
        return self.__dict__

class EventBuilder:
    """Builder pattern"""
    def __init__(self,event=None):
        self._event = event if event is not None else Event()
    def as_calendar_event(self):
        setattr(self, 'king',"calendar#event")
    def with_summary(self,summary:str):
        setattr(self._event, 'summary', summary)
        return self
    def with_description(self,description:str):
        setattr(self._event, 'description', description)
        return self
    def with_location(self,location:str):
        setattr(self._event, 'location', location)
        return self

    def _check_date_format(self,dateTime:str):
        try:
            return datetime.fromisoformat(dateTime).isoformat()
        except ValueError:
            raise ValueError('Invalid date format')
    def with_start_date(self, dateTime:str):
        """Proper format: 2026-07-01T15:31:00+00:00"""
        """:raise ValueError if format non valid """
        self._event.start['dateTime'] = self._check_date_format(dateTime)
        return self
    def with_end_date(self, dateTime:str):
        """Proper format: 2026-07-01T15:31:00+00:00"""
        """:raise ValueError if format non valid """
        self._event.end['dateTime'] = self._check_date_format(dateTime)
        return self
    def with_attendees(self,attendees_emails:list | str):
        """Proper format: [<EMAIL>,<EMAIL>]"""
        if  isinstance(attendees_emails,str):
            attendees_emails = attendees_emails.split(',')
        for email in attendees_emails:
            temp = email.split('@')
            if len(temp) != 2 or len(temp[0])==0 or len(temp[1])==0 or len(temp[1].split('.'))==0:
                raise ValueError('Invalid email format')
        setattr(self._event, 'attendees',
                [{'email':email} for email in attendees_emails])
        return self

    def with_color_id(self, color_id: str):
        """Proper format: not Hex, must be in [1,2,3,4,5,6,7,8,9]"""
        setattr(self._event, 'colorId', color_id)
        return self
    def with_reminders(self,useDefault:bool,overrides:list[dict[str,str | int]]):
        """useDefault: use default reminders,
        overrides: [{'method':'popup' | 'email',  'minutes':int>=0}]"""
        for x in overrides:
            if not 'method' in x:
                raise ValueError('invalid override no method')
            else:
                if not x['method'] in ('popup','email'):
                    raise ValueError('invalid override method')
            if not 'minutes' in x:
                raise ValueError('invalid override no minutes')
            else:
                if not isinstance(x['minutes'],int) or x['minutes'] < 0:
                    raise ValueError('invalid override minutes')
        setattr(self._event, 'reminders', {
            'useDefault': useDefault,
            'overrides': overrides
        })
        return self
    def add_reminder(self,method:str,minutes:int):
        """method: 'popup' | 'email',  minutes: int>=0"""
        if not method in ('popup','email'):
            raise ValueError('invalid reminder method')
        if minutes < 0:
            raise ValueError('invalid reminder minutes')
        reminder = {'method':method,'minutes':minutes}
        if hasattr(self._event,'reminders'):
            temp = self._event.reminders
            temp['overrides'].append(reminder)
            return self
        else:
            return self.with_reminders(False,[reminder])

    def with_description(self,description:str):
        setattr(self._event, 'description', description)
        return self
    def with_location(self,location:str):
        setattr(self._event, 'location', location)
        return self
    def with_status(self, status:str):
        if status not in ['confirmed','tentative','cancelled']:
            raise ValueError(f'status must be confirmed, tentative or cancelled')
        setattr(self._event, 'status', status)
    def with_creator(self,email:str,displayName:str=None):
        setattr(self._event, 'creator', {
            'email': email,
            'displayName': displayName if displayName else ''
        })
    def with_anyoneCanAddSelf(self,b:bool):
        setattr(self._event, 'anyoneCanAddSelf', b)
        return self
    def with_guestsCanInviteOthers(self,b:bool):
        setattr(self._event, 'guestsCanInviteOthers', b)
        return self
    def with_guestsCanModify(self,b:bool):
        setattr(self._event, 'guestsCanModify', b)
    def with_guestsCanSeeOtherGuests(self,b:bool):
        setattr(self._event, 'guestsCanSeeOtherGuests', b)
        return self
    def build(self)->Event:
        if not hasattr(self._event, 'summary'):
            raise ValueError(f'event summary is required')
        if not hasattr(self._event,'start'):
            raise ValueError(f'event start is required')
        if not hasattr(self._event,'end'):
            raise ValueError(f'event end is required')
        return self._event


