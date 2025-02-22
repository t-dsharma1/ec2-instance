from dataclasses import dataclass
from typing import Optional, Union

from dataclasses_json import dataclass_json

__all__ = ["DialogueFeatures", "CustomerFeatures", "LLMFeatures"]


# @dataclass
# class Sentiment:
#     positive: int
#     neutral: int
#     negative: int


@dataclass_json
@dataclass
class DialogueFeatures:
    language: Optional[str] | None = None
    tone: Optional[str] | None = None
    sentiment: Optional[str] | None = None
    discussed_plans: Optional[Union[str, list]] = None
    summary: Optional[str] | None = None


@dataclass_json
@dataclass
class CustomerFeatures:
    data_needs: Optional[Union[str, list]] = None
    type_of_plan: Optional[str] | None = None
    number_of_lines: Optional[str] | None = None
    otts: Optional[str] | None = None
    pin_code: Optional[str] | None = None
    existing_services: Optional[str] | None = None
    other_needs: Optional[list[str]] | None = None


@dataclass_json
@dataclass
class LLMFeatures:
    state_name: str | None = None
    next_goal: str | None = None
    reasoning: str | None = None
