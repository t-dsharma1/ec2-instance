from dataclasses import dataclass

from dataclasses_json import dataclass_json

from ._features import CustomerFeatures, DialogueFeatures, LLMFeatures

__all__ = ["Response"]


@dataclass_json
@dataclass
class Response:
    llm_response: str
    llm_features: LLMFeatures
    dialogue_features: DialogueFeatures | None = None
    customer_features: CustomerFeatures | None = None
    conversation_ended_flag: bool = False
