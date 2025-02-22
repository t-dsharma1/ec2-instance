import datetime
import enum
from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from genie_dao.datamodel._prompts import PromptMessage
from genie_dao.datamodel._roles import Role

__all__ = ["MessageType", "Message", "InputMessage", "OutputMessage"]


@dataclass_json
class MessageType(str, enum.Enum):
    input = "INPUT"
    output = "OUTPUT"


@dataclass_json
@dataclass
class Message:
    content: Optional[str]
    sent_at: Optional[datetime.datetime]
    type: Optional[MessageType]


@dataclass_json
@dataclass
class InputMessage(Message):
    content: Optional[str] = None
    language: Optional[str] = None
    sent_at: Optional[datetime.datetime] = datetime.datetime.now()
    type: Optional[MessageType] = MessageType.input

    def get_user_prompt(
        self,
    ) -> PromptMessage:
        return PromptMessage(role=Role.USER, content=self.content)


@dataclass_json
@dataclass
class OutputMessage(Message):
    content: str
    sent_at: datetime.datetime = datetime.datetime.now()
    type: MessageType = MessageType.output
