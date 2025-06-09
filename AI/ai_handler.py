import os
from google import genai
from datetime import datetime
from AI.event_schema import EventAction
from dotenv import load_dotenv
import json
import re

load_dotenv()
AI_TOKEN = os.getenv("GOOGLE_AI_API_KEY")

client = genai.Client(api_key=AI_TOKEN)

def check_mails(emails):
    EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
    return [email for email in emails if EMAIL_REGEX.match(email)]


def ai_parse_text(user_input):
    if (user_input):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Dzisiejsza data to: {datetime.now()}. {user_input}",
            config={
                "response_mime_type": "application/json",
                "response_schema": EventAction
            },
        )

        data = json.loads(response.text)

        data["attendees_emails"] = check_mails(data["attendees_emails"])

        data["new_attendees_emails"] = check_mails(data["new_attendees_emails"])

        return data




if __name__ == "__main__":
    print(ai_parse_text("dodaj na jutro spotkanie z Mateuszem od 10 do 12"))
