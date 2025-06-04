from pydantic import BaseModel
import enum
from datetime import datetime

class EventType(enum.Enum):
  ADD = "Add"
  EDIT = "Edit"
  REMOVE = "Remove"
  UNKNOWN = 'Unknown'


class EventAction(BaseModel):
    event_type: EventType
    event_name: None | str
    data_start: datetime
    data_end: datetime