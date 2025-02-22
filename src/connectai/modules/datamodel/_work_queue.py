import datetime
from dataclasses import dataclass

from dataclasses_json import dataclass_json

__all__ = ["WorkQueueItem"]


@dataclass_json
@dataclass
class WorkQueueItem:
    chat_message: str
    chat_timestamp: datetime.datetime
    from_number: str
    to_number: str
    business_id: str
    session_id: str
    source: str
