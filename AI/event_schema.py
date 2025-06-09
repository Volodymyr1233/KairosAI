from pydantic import BaseModel, field_validator
import enum
from datetime import datetime
import re


class EventType(enum.Enum):
  ADD = "Add"
  EDIT = "Edit"
  REMOVE = "Remove"
  SHOW = "Show"
  UNKNOWN = 'Unknown'


class EventAction(BaseModel):
    event_type: EventType
    event_name: str
    new_event_name: str | None
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
    remind_minutes: int | None
    new_remind_minutes: int | None
    event_color: None | str
    new_event_color: None | str