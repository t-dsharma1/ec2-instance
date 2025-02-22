from datetime import datetime

import pytest

from connectai.modules.datamodel import Conversation, InputMessage, MessageType


@pytest.fixture(scope="class")
def user_messages() -> Conversation:
    hello_msg = InputMessage(
        content="Hello!", type=MessageType.input, sent_at=datetime.fromisoformat("2024-01-31T15:30:00")
    )
    bye_msg = InputMessage(
        content="Bye!", type=MessageType.input, sent_at=datetime.fromisoformat("2024-01-31T15:30:00")
    )
    chat_history = [hello_msg, bye_msg]
    return Conversation(history=chat_history)


@pytest.fixture(scope="class")
def assistant_messages() -> Conversation:
    hi_msg = InputMessage(
        content="Hi there!", type=MessageType.output, sent_at=datetime.fromisoformat("2024-01-31T15:30:00")
    )
    bye_msg = InputMessage(
        content="Bye-Bye!", type=MessageType.output, sent_at=datetime.fromisoformat("2024-01-31T15:30:00")
    )
    chat_history = [hi_msg, bye_msg]
    return Conversation(history=chat_history)
