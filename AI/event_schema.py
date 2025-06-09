from pydantic import BaseModel
import enum
from datetime import datetime


class EventType(enum.Enum):
  ADD = "Add"
  EDIT = "Edit"
  REMOVE = "Remove"
  SHOW = "Show"
  UNKNOWN = 'Unknown'

class EventColor(enum.Enum):
    jasnoniebieski = "jasnoniebieski"
    mietowy = "miętowy"
    fioletowy = "fioletowy"
    lososiowy = "łososiowy"
    zolty = "żółty"
    pomaranczowy = "pomarańczowy"
    turkusowy = "turkusowy"
    szary = "szary"
    niebieski = "niebieski"
    zielony = "zielony"
    czerwony = "czerwony"

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
    event_color: None | EventColor
    new_event_color: None | EventColor