from pydantic import BaseModel, EmailStr
import enum
from datetime import datetime

class EventType(enum.Enum):
  ADD = "Add"
  EDIT = "Edit"
  REMOVE = "Remove"
  SHOW = "Show"
  UNKNOWN = 'Unknown'


class EventAction(BaseModel):
    event_type: EventType
    event_name: str
    new_event_name: None | str
    event_description: None | str
    new_event_description: None | str
    data_start: datetime
    new_data_start: datetime | None
    data_end: datetime
    new_data_end: datetime | None
    location: None | str
    new_location: None | str
    attendees_emails: list[str]
    new_attendees_emails: list[str]
    event_color: None | str
    new_event_color: None | str
