from pydantic import BaseModel
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
    event_name: None | str
    new_event_name_for_update: None | str
    data_start: datetime
    data_end: datetime