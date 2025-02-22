import datetime
import enum
import json
from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json
from pydantic import BaseModel

from ._conversations import ConversationContext
from ._features import CustomerFeatures, DialogueFeatures, LLMFeatures
from ._messaging import InputMessage, OutputMessage

__all__ = [
    "APIChatResponseRequestPayload",
    "APIRequestJSONEncoder",
    "APIBroadbandResponseRequestPayload",
    "AgentResponseRequestPayload",
    "AgentResponsePayload",
    "EndConversationRequestPayload",
]


@dataclass_json
@dataclass
class AgentResponseRequestPayload(BaseModel):
    # TODO: Update this to be a hash as it represents the name of the flow for time being
    flow_id: str
    user_id: str
    has_opt_in: Optional[bool] = False
    force_new_conversation: Optional[bool] = False
    conversation_pk: Optional[str] = None
    conversation_context: ConversationContext = None
    message: InputMessage = None
    sent_datetime: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True


@dataclass_json
@dataclass
class EndConversationRequestPayload:
    conversation_id: str


@dataclass_json
@dataclass
class StartConversationRequestPayload:
    flow_id: str
    user_id: str


@dataclass_json
@dataclass
class AgentResponsePayload:
    conversation_id: str = None
    message_id: str = None
    message: OutputMessage = None
    conversation_features: DialogueFeatures = None
    customer_features: CustomerFeatures = None
    conversation_state: str = None
    conversation_ended_flag: bool = False
    llm_features: LLMFeatures = None
    response_completed: bool = False
    sent_datetime: datetime.datetime = datetime.datetime.now()


@dataclass_json
@dataclass
class APIChatResponseRequestPayload:
    user_id: str
    content: str
    # configs: dict[str, str]


@dataclass_json
@dataclass
class APIBroadbandResponseRequestPayload:
    user_id: str
    content: str
    first_reach: bool


class APIRequestJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, enum.Enum):
            return obj.value
        else:
            return obj.__dict__
