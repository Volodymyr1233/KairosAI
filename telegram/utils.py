from datetime import datetime
from zoneinfo import ZoneInfo
from AI.event_schema import EventType
from GoogleAPI.Event import EventBuilder
from GoogleAPI.GoogleCalendarAPI import addEvent, getEvents, updateEvent
from Credentials.CredentialsFuntions_online import get_user_credential
from dateutil.parser import parse
from GoogleAPI.Event import Event


def convert_data_time(date_time):
    return parse(date_time).replace(tzinfo=ZoneInfo("Europe/Warsaw")).isoformat()

def parse_json_to_bot_answer(data):
    event_type = data["event_type"]
    if (event_type == EventType.UNKNOWN.value):
        return None

    event_name = data["event_name"]
    bot_answer_result = (
        f"<b>Typ eventu</b>: {change_event_type(event_type)}\n"
        f"<b>Nazwa eventu</b>: {event_name}\n"
    )

    if (event_type == EventType.EDIT.value):
        if (data["new_event_name"]):
            bot_answer_result += f'<b>Nowa nazwa ewentu</b>: {data["new_event_name"]}\n'
        if (data["new_event_description"]):
            bot_answer_result += f'<b>Nowy opis wydarzenia</b>: {data["new_event_description"]}\n'
        if (data["new_event_color"]):
            bot_answer_result += f'<b>Nowy kolor ewentu: </b>: {data["new_event_color"]}\n'
        if (data["new_data_start"]):
            iso_new_start_date = datetime.fromisoformat(data["new_data_start"])
            formatted_new_start_date = iso_new_start_date.strftime("%H:%M %d.%m.%Y")
            bot_answer_result += f"<b>Nowa data i czas początku</b>: {formatted_new_start_date}\n"
        if (data["new_data_end"]):
            iso_new_end_date = datetime.fromisoformat(data["new_data_end"])
            formatted_new_end_date = iso_new_end_date.strftime("%H:%M %d.%m.%Y")
            bot_answer_result += f"<b>Nowa data i czas końca</b>: {formatted_new_end_date}\n"
        if (data["new_location"]):
            bot_answer_result += f'<b>Nowa lokalizacja</b>: {data["new_location"]}\n'
        if (data["new_attendees_emails"]):
            bot_answer_result += f'<b>Nowa lista email zaproszonych</b>: {[email.strip() for email in data["new_attendees_emails"]]}\n'
        if (data["new_remind_minutes"]):
            bot_answer_result += f'<b>Nowe przypomnienie</b>: {data["new_remind_minutes"]} minut przed\n'



    else:
        if (data["event_description"]):
            bot_answer_result += f'<b>Opis wydarzenia</b>: {data["event_description"]}\n'
        iso_start_date = datetime.fromisoformat(data["data_start"])
        formatted_start_date = iso_start_date.strftime("%H:%M %d.%m.%Y")

        bot_answer_result += f"<b>Data i czas początku</b>: {formatted_start_date}\n"

        iso_end_date = datetime.fromisoformat(data["data_end"])
        formatted_end_date = iso_end_date.strftime("%H:%M %d.%m.%Y")

        bot_answer_result += f"<b>Data i czas końca</b>: {formatted_end_date}\n"

        if (data["event_color"]):
            bot_answer_result += f'<b>Kolor ewentu: </b>: {data["event_color"]}\n'

        if (data["location"]):
            bot_answer_result += f'<b>Lokalizacja</b>: {data["location"]}\n'

        if (data["attendees_emails"]):
            bot_answer_result += f'<b>Lista email zaproszonych</b>: {[email.strip() for email in data["attendees_emails"]]}\n'

        if (data["remind_minutes"]):
            bot_answer_result += f'<b>Przopomnienie</b>: {data["remind_minutes"]} minut przed\n'

    return bot_answer_result

def manage_events(parsed_ai_json, user_id):
    event_name = parsed_ai_json["event_name"]
    event_description = parsed_ai_json["event_description"]
    data_start = convert_data_time(parsed_ai_json["data_start"])
    data_end = convert_data_time(parsed_ai_json["data_end"])
    location = parsed_ai_json["location"]
    color_str = parsed_ai_json["event_color"]
    attendees_list = parsed_ai_json["attendees_emails"]
    reminder = 0
    if (parsed_ai_json["remind_minutes"]):
        reminder =  int(parsed_ai_json["remind_minutes"])
    match parsed_ai_json["event_type"]:
        case EventType.ADD.value:
            print(user_id)
            e = (EventBuilder().with_summary(event_name).with_start_date(
            data_start).with_end_date(data_end).with_attendees(attendees_list).add_reminder("email", reminder).with_description(event_description).with_location(location).with_color_id(color_to_number(color_str))).build()
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

COLOR_SYMBOLS = {
    "1": ("🔵", "Jasnoniebieski"),
    "2": ("💚", "Miętowy"),
    "3": ("💜", "Fioletowy"),
    "4": ("❤️", "Łososiowy"),
    "5": ("💛", "Żółty"),
    "6": ("🟧", "Pomarańczowy"),
    "7": ("🟦", "Turkusowy"),
    "8": ("⬜", "Szary"),
    "9": ("🔷", "Niebieski"),
    "10": ("🟢", "Zielony"),
    "11": ("🟥", "Czerwony"),
}

def format_datetime(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return dt_str or "Brak daty"

def construct_events(events, title="Twoje wydarzenia"):
    if not events:
        return "🔔 Nie masz żadnych wydarzeń w kalendarzu."

    events_string = f"<b>📅 {title}:</b>\n\n"

    for i, event in enumerate(events):
        event_data = event.to_dict()
        summary = event_data.get("summary", "⸺ Bez tytułu")
        location = event_data.get("location")
        description = event_data.get("description")
        start_raw = event_data.get("start", {}).get("dateTime") or event_data.get("start", {}).get("date")
        end_raw = event_data.get("end", {}).get("dateTime") or event_data.get("end", {}).get("date")
        color_id = event_data.get("colorId")
        attendees_emails = event_data.get("attendees_emails")

        color_emoji, color_name = COLOR_SYMBOLS.get(color_id, ("📌", "Domyślny"))

        start = format_datetime(start_raw)
        end = format_datetime(end_raw) if end_raw else None

        events_string += f"<b>{i+1}. {color_emoji} {summary}</b>\n"
        events_string += f"   🕒 Początek: <i>{start}</i>\n"
        if end:
            events_string += f"   🕓 Koniec: <i>{end}</i>\n"

        if location:
            events_string += f"   📍 {location}\n"
        if description:
            events_string += f"   📝 {description.strip()}\n"
        if attendees_emails:
            events_string += f"   📩 {[email for email in attendees_emails]}\n"

        if event_data.get("remind_minutes"):
            events_string += f"   ⏰ {event_data.get('remind_minutes')}\n"
        events_string += "\n"


    return events_string

def color_to_number(color):
    COLOR_MAP = {
        "jasnoniebieski": "1",
        "miętowy": "2",
        "fioletowy": "3",
        "łososiowy": "4",
        "żółty": "5",
        "pomarańczowy": "6",
        "turkusowy": "7",
        "szary": "8",
        "niebieski": "9",
        "zielony": "10",
        "czerwony": "11"
    }

    return COLOR_MAP.get(color, "9")

def update_event(user_id, event: Event, parsed_ai_json):
    event_build = EventBuilder(event)
    if (parsed_ai_json["new_event_name"]):
        event_build.with_summary(parsed_ai_json["new_event_name"])
    if (parsed_ai_json["new_event_description"]):
        event_build.with_description(parsed_ai_json["new_event_description"])
    if (parsed_ai_json["new_data_start"]):
        event_build.with_start_date(convert_data_time(parsed_ai_json["new_data_start"]))
    if (parsed_ai_json["new_data_end"]):
        event_build.with_end_date(convert_data_time(parsed_ai_json["new_data_end"]))
    if (parsed_ai_json["new_location"]):
        event_build.with_location(parsed_ai_json["new_location"])
    if (parsed_ai_json["new_event_color"]):
        event_build.with_color_id(color_to_number(parsed_ai_json["new_event_color"]))
    if (parsed_ai_json["new_attendees_emails"]):
        event_build.with_attendees(parsed_ai_json["new_attendees_emails"])
    if (parsed_ai_json["new_remind_minutes"]):
        event_build.add_reminder("email", parsed_ai_json["new_remind_minutes"])
    e = event_build.build()
    print(e.to_dict())
    updateEvent(get_user_credential(user_id), e)

def generate_indexes(arr):
    return list([str(i) for i in range(1, len(arr) + 1)])

def change_event_type(event_type):
    match event_type:
        case EventType.ADD.value:
            return "Dodaj event"
        case EventType.REMOVE.value:
            return "Usuń event"
        case EventType.EDIT.value:
            return "Edytuj event"
        case EventType.SHOW.value:
            return "Pokaż eventy"

