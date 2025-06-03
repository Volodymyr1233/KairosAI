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
    def __init__(self,event=Event()):
        self._event = event
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
            return ValueError('Invalid date format')
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
        """Proper format: <EMAIL>,<EMAIL>"""
        if not isinstance(attendees_emails,list):
            attendees_emails = attendees_emails.split(',')
        setattr(self._event, 'attendees',
                [{'email':email} for email in attendees_emails])
        return self

    def with_color_id(self, color_id: str):
        setattr(self._event, 'colorId', color_id)
        return self
    def with_reminders(self,useDefault:bool,overrides:dict[str,str]):
        setattr(self._event, 'reminders', {
            'useDefault': useDefault,
            'overrides': overrides
        })
        return self
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
    def build(self):
        if not hasattr(self._event, 'summary'):
            raise ValueError(f'event summary is required')
        if not hasattr(self._event,'start'):
            raise ValueError(f'event start is required')
        if not hasattr(self._event,'end'):
            raise ValueError(f'event end is required')
        return self._event




"""
        {
          "kind": "calendar#event",
          "etag": etag,
          "id": string,
          "status": string,
          "htmlLink": string,
          "created": datetime,
          "updated": datetime,
          "summary": string,
          "description": string,
          "location": string,
          "colorId": string,
          "creator": {
            "id": string,
            "email": string,
            "displayName": string,
            "self": boolean
          },
          "organizer": {
            "id": string,
            "email": string,
            "displayName": string,
            "self": boolean
          },
          "start": {
            "date": date,
            "dateTime": datetime,
            "timeZone": string
          },
          "end": {
            "date": date,
            "dateTime": datetime,
            "timeZone": string
          },
          "endTimeUnspecified": boolean,
          "recurrence": [
            string
          ],
          "recurringEventId": string,
          "originalStartTime": {
            "date": date,
            "dateTime": datetime,
            "timeZone": string
          },
          "transparency": string,
          "visibility": string,
          "iCalUID": string,
          "sequence": integer,
          "attendees": [
            {
              "id": string,
              "email": string,
              "displayName": string,
              "organizer": boolean,
              "self": boolean,
              "resource": boolean,
              "optional": boolean,
              "responseStatus": string,
              "comment": string,
              "additionalGuests": integer
            }
          ],
          "attendeesOmitted": boolean,
          "extendedProperties": {
            "private": {
              (key): string
            },
            "shared": {
              (key): string
            }
          },
          "hangoutLink": string,
          "conferenceData": {
            "createRequest": {
              "requestId": string,
              "conferenceSolutionKey": {
                "type": string
              },
              "status": {
                "statusCode": string
              }
            },
            "entryPoints": [
              {
                "entryPointType": string,
                "uri": string,
                "label": string,
                "pin": string,
                "accessCode": string,
                "meetingCode": string,
                "passcode": string,
                "password": string
              }
            ],
            "conferenceSolution": {
              "key": {
                "type": string
              },
              "name": string,
              "iconUri": string
            },
            "conferenceId": string,
            "signature": string,
            "notes": string,
          },
          "gadget": {
            "type": string,
            "title": string,
            "link": string,
            "iconLink": string,
            "width": integer,
            "height": integer,
            "display": string,
            "preferences": {
              (key): string
            }
          },
          "anyoneCanAddSelf": boolean,
          "guestsCanInviteOthers": boolean,
          "guestsCanModify": boolean,
          "guestsCanSeeOtherGuests": boolean,
          "privateCopy": boolean,
          "locked": boolean,
          "reminders": {
            "useDefault": boolean,
            "overrides": [
              {
                "method": string,
                "minutes": integer
              }
            ]
          },
          "source": {
            "url": string,
            "title": string
          },
          "workingLocationProperties": {
            "type": string,
            "homeOffice": (value),
            "customLocation": {
              "label": string
            },
            "officeLocation": {
              "buildingId": string,
              "floorId": string,
              "floorSectionId": string,
              "deskId": string,
              "label": string
            }
          },
          "outOfOfficeProperties": {
            "autoDeclineMode": string,
            "declineMessage": string
          },
          "focusTimeProperties": {
            "autoDeclineMode": string,
            "declineMessage": string,
            "chatStatus": string
          },
          "attachments": [
            {
              "fileUrl": string,
              "title": string,
              "mimeType": string,
              "iconLink": string,
              "fileId": string
            }
          ],
          "birthdayProperties": {
            "contact": string,
            "type": string,
            "customTypeName": string
          },
          "eventType": string
        }
        """



