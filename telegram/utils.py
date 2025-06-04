from datetime import datetime
from AI.event_schema import EventType

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
