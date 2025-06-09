from sympy.testing.pytest import Failed

from GoogleAPI import Event
from GoogleAPI.Event import EventBuilder
import pytest

def test_creation():
    event_d = {
        'id': 'abc123def456',
        'status': 'confirmed',
        'htmlLink': 'https://www.google.com/calendar/event?eid=abc123def456',
        'summary': 'Spotkanie zespołu',
        'description': 'Omówienie sprintu i postępów w projekcie.',
        'location': 'Sala 101, Biuro',
        'creator': {
            'email': 'jan.kowalski@example.com',
            'displayName': 'Jan Kowalski',
            'self': True
        },
        'organizer': {
            'email': 'jan.kowalski@example.com',
            'displayName': 'Jan Kowalski',
            'self': True
        },
        'start': {
            'dateTime': '2026-07-01T15:30:00+02:00',
            'timeZone': 'Europe/Warsaw'
        },
        'end': {
            'dateTime': '2026-07-01T16:30:00+02:00',
            'timeZone': 'Europe/Warsaw'
        },
        'recurrence': [
            'RRULE:FREQ=WEEKLY;COUNT=4'
        ],
        'attendees': [
            {
                'email': 'anna.nowak@example.com',
                'displayName': 'Anna Nowak',
                'responseStatus': 'accepted'
            }
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 10},
                {'method': 'email', 'minutes': 60}
            ]
        }
    }
    event = Event.Event(event_d)
    for k,v in event_d.items():
        assert getattr(event, k) == v
    try:
        builder = EventBuilder()
        builder.with_summary('summary')
        builder.with_description('description')
        builder.with_location('location')
        builder.with_start_date('2026-07-01T15:31:00+00:00')
        builder.with_end_date('2026-07-01T16:31:00+00:00')
        builder.with_color_id('3')
        builder.with_attendees(['email1@gmail.com','email2@gmail.com','email3@gmail.com'])
        builder.add_reminder('popup',10)
        builder.add_reminder('email',60)
        builder.with_status('confirmed')
        builder.with_creator('creator@gmail.com','creator')
        builder.with_anyoneCanAddSelf(True)
        builder.with_guestsCanInviteOthers(True)
        builder.with_guestsCanSeeOtherGuests(False)
        builder.with_guestsCanModify(False)
        event = builder.build()
        assert event.summary == 'summary'
        assert event.description == 'description'
        assert event.location =='location'
        assert event.start['dateTime'] == '2026-07-01T15:31:00+00:00'
        assert event.end['dateTime'] == '2026-07-01T16:31:00+00:00'
        assert event.attendees == [
            {'email':'email1@gmail.com'},
            {'email':'email2@gmail.com'},
            {'email':'email3@gmail.com'},
        ]
        assert event.colorId == '3'
        assert event.reminders['overrides'] == [
            {
                'method': 'popup',
                'minutes': 10
            },
            {
                'method': 'email',
                'minutes': 60
            }
        ]
        assert event.status == 'confirmed'
        assert event.creator == {
            'email': 'creator@gmail.com',
            'displayName': 'creator',
        }
        assert event.anyoneCanAddSelf == True
        assert event.guestsCanInviteOthers == True
        assert event.guestsCanSeeOtherGuests == False
        assert event.guestsCanModify == False
        try:
            EventBuilder().with_start_date('1234-07-01T15:32:12:a:00')
            assert False
        except ValueError:
            pass
        try:
            EventBuilder().with_end_date('asdasd')
            assert False
        except ValueError:
            pass
        try:
            EventBuilder().with_attendees(['asdsadsd'])
            assert False
        except ValueError:
            pass


    except AttributeError as e:
        pytest.fail(f'No attribute {e.name}, {e.args}')





