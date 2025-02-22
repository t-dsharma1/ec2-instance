from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel


class BaseMessage(BaseModel):
    name: Optional[str] = None
    client_id: Optional[str] = None
    id: Optional[str] = None
    connection_id: Optional[str] = None
    connection_key: Optional[str] = None
    encoding: Optional[str] = None
    timestamp: Optional[str] = None
    extras: Optional[dict] = None
    data: Optional[str] = None


class BaseChannel(ABC, BaseModel):
    @abstractmethod
    def __str__(self):
        raise NotImplementedError()
