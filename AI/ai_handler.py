import os
from google import genai
from datetime import datetime
from AI.event_schema import EventAction
from dotenv import load_dotenv
import json

load_dotenv()
AI_TOKEN = os.getenv("GOOGLE_AI_API_KEY")

client = genai.Client(api_key=AI_TOKEN)

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

        return data



if __name__ == "__main__":
    print(ai_parse_text("Weź mi zrób spotkanie na jutro o 10")["data_start"])
