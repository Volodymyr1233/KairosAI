from datetime import datetime, timezone
from AI.event_schema import EventType
from GoogleAPI.Event import EventBuilder
from GoogleAPI.GoogleCalendarAPI import addEvent, getEvents, updateEvent
from Credentials.CredentialsFunctions import get_user_credential
from dateutil.parser import parse
from GoogleAPI.Event import Event

def parse_json_to_bot_answer(data):
    event_type = data["event_type"]
    if (event_type == EventType.UNKNOWN.value):
        return None

    event_name = data["event_name"]
    iso_start_date = datetime.fromisoformat(data["data_start"])
    iso_end_date = datetime.fromisoformat(data["data_end"])

    formatted_start_date = iso_start_date.strftime("%d.%m.%Y")
    formatted_start_time = iso_start_date.strftime("%H:%M")

    formatted_end_date = iso_end_date.strftime("%d.%m.%Y")
    formatted_end_time = iso_end_date.strftime("%H:%M")
    bot_answer = (
        f"<b>Typ eventu</b>: {event_type}\n"
        f"<b>Nazwa eventu</b>: {event_name}\n"
        f"<b>Data i czas początku</b>: {formatted_start_time} {formatted_start_date}\n"
        f"<b>Data i czas końca</b>: {formatted_end_time} {formatted_end_date}"
    )

    return bot_answer

def manage_events(parsed_ai_json, user_id):
    event_name = parsed_ai_json["event_name"]
    data_start = parsed_ai_json["data_start"]
    data_end = parsed_ai_json["data_end"]
    match parsed_ai_json["event_type"]:
        case EventType.ADD.value:
            print(user_id)
            e = (EventBuilder().with_summary(event_name).with_start_date(
            data_start).with_end_date(data_end)).build()
            addEvent(get_user_credential(user_id), e)
            return "Ewent został dodany"
        case EventType.SHOW.value:
            iso_data_start = parse(data_start).isoformat()
            iso_data_end = parse(data_end).isoformat()
            events = getEvents(get_user_credential(user_id), time_min=iso_data_start, time_max=iso_data_end)
            return events
        case EventType.REMOVE.value:
            removed_events = getEvents(get_user_credential(user_id), query=event_name)
            print(removed_events)
            return removed_events
        case EventType.EDIT.value:
            updated_events = getEvents(get_user_credential(user_id), query=event_name)
            return updated_events

def construct_events(events):
    events_string = "Twoje ewenty:\n"
    for i in range(len(events)):
        print(type(events[i]))
        events_string += f"{i+1} - {events[i].to_dict()['summary']}\n"

    return events_string

def update_event(user_id, event: Event, parsed_ai_json):
    new_event_name_to_update = parsed_ai_json["new_event_name_for_update"]
    data_start = parsed_ai_json["data_start"]
    data_end = parsed_ai_json["data_end"]
    e = (EventBuilder(event).with_summary(new_event_name_to_update).with_start_date(
        data_start).with_end_date(data_end)).build()
    updateEvent(get_user_credential(user_id), e)

def generate_indexes(arr):
    return list([str(i) for i in range(1, len(arr) + 1)])