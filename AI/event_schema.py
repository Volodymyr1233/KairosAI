from pydantic import BaseModel
from datetime import datetime
import enum


class EventType(enum.Enum):
    ADD = "Add"
    EDIT = "Edit"
    REMOVE = "Remove"
    SHOW = "Show"
    UNKNOWN = "Unknown"


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


class AddEvent(BaseModel):
    event_name: str
    event_description: str | None
    data_start: datetime
    data_end: datetime
    location: str | None
    attendees_emails: list[str]
    remind_minutes: int | None
    event_color: EventColor | None


class ShowAndRemoveEvent(BaseModel):
    event_name: str | None
    event_description: str | None
    data_start: datetime | None
    data_end: datetime | None
    location: str | None
    attendees_emails: list[str]
    remind_minutes: int | None
    event_color: EventColor | None


class EditEvent(BaseModel):
    event_name: str
    data_start: datetime | None
    data_end: datetime | None
    new_event_name: str | None
    new_event_description: str | None
    new_data_start: datetime | None
    new_data_end: datetime | None
    new_location: str | None
    new_attendees_emails: list[str]
    new_remind_minutes: int | None
    new_event_color: EventColor | None
