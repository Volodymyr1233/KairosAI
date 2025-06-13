import os
from google import genai
from datetime import datetime
from AI.event_schema import EventType, AddEvent, ShowEvent, EditEvent, RemoveEvent
from dotenv import load_dotenv
import json
import re

load_dotenv()
AI_TOKEN = os.getenv("GOOGLE_AI_API_KEY")

client = genai.Client(api_key=AI_TOKEN)

def check_mails(emails):
    EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
    return [email for email in emails if EMAIL_REGEX.match(email)]

def generate_ai_model(schema, user_input):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"Dzisiejsza data to: {datetime.now()}.{user_input}",
        config={
            "response_mime_type": "application/json",
            "response_schema": schema
        },
    )

    return response


def detect_event_type(user_input):
    response = generate_ai_model(EventType, user_input)
    return response.text.strip('"')



def ai_parse_text(user_input):
    event_type = detect_event_type(user_input)
    print(event_type)
    result = {}
    match event_type:
        case EventType.ADD.value:
            response = generate_ai_model(AddEvent, user_input)
            data = json.loads(response.text)
            result = {"event_type": event_type, **data}
        case EventType.SHOW.value:
            response = generate_ai_model(ShowEvent, user_input)
            data = json.loads(response.text)
            result = {"event_type": event_type, **data}
        case EventType.EDIT.value:
            response = generate_ai_model(EditEvent, user_input)
            data = json.loads(response.text)
            result = {"event_type": event_type, **data}
        case EventType.REMOVE.value:
            response = generate_ai_model(RemoveEvent, user_input)
            data = json.loads(response.text)
            result = {"event_type": event_type, **data}
        case EventType.UNKNOWN.value:
            return {"event_type": event_type}

    if "attendees_emails" in result:
        result["attendees_emails"] = check_mails(result["attendees_emails"])
    if "new_attendees_emails" in result:
        result["new_attendees_emails"] = check_mails(result["new_attendees_emails"])

    return result




if __name__ == "__main__":
    print(ai_parse_text("pokaż wszystkie ewenty na dzisiaj"))
