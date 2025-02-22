from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

from dataclasses_json import dataclass_json

T = TypeVar("T")

__all__ = ["PagedResponseSchema", "ConversationFilter"]


@dataclass_json
@dataclass
class PagedResponseSchema(Generic[T]):
    """Response schema for any paged API."""

    total: int
    results: list[T]
    next: Optional[int] = None
    previous: Optional[int] = None
    filters: Optional[dict[str, list[str]]] = None


@dataclass_json
@dataclass
class ConversationFilter:
    """Filter for ConversationTable."""

    PK: Optional[str] = None
    ai_state_name: Optional[str] = None
    ai_state_datetime: Optional[str] = None
