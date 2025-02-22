import json
import os
import re
from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from connectai.handlers.api.routers.telcoapi import agent_response
from connectai.handlers.queue.worker import (
    create_new_user,
    generate_payload,
    handle_user_message,
    process_message,
)
from connectai.modules.datamodel import (
    AgentResponsePayload,
    OutputMessage,
    WorkQueueItem,
)


@pytest.fixture
def sample_message():
    return {
        "Body": json.dumps(
            {
                "from_number": "12345",
                "to_number": "67890",
                "chat_message": "Sample message 123456",
                "session_id": "session123",
                "business_id": "business123",
                "source": "none",
                "chat_timestamp": "2024-03-15T15:00:59.078161",
            }
        )
    }


@pytest.mark.integration
@patch("connectai.handlers.queue.worker.boto3.resource")
@patch("connectai.handlers.queue.worker.agent_response")
async def test_process_message(mock_agent_response, mock_boto3_resource, sample_message):
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table
    mock_agent_response.return_value = AgentResponsePayload(
        conversation_id="1",
        message_id="1",
        message=OutputMessage(content="hi"),
    )
    queue_message = WorkQueueItem(**json.loads(sample_message["Body"]))
    response = await process_message(queue_message)
    assert response == "hi"


def test_handle_user_message():
    mock_table = MagicMock()
    mock_table.get_item.return_value = {"Item": {"is_first_message": True}}

    assert handle_user_message("12345", "reset", mock_table, "2024-05-21T12:00:00") is False
    assert handle_user_message("12345", "hello", mock_table, "2024-05-21T12:00:00") is False

    mock_table.get_item.return_value = {}
    assert handle_user_message("12345", "hello", mock_table, "2024-05-21T12:00:00") is True


def test_create_new_user():
    mock_table = MagicMock()
    create_new_user("12345", mock_table, "2024-05-21T12:00:00")
    assert mock_table.put_item.called


def test_generate_payload():
    payload = generate_payload("Hello", "12345", True)
    assert payload["flow_id"] == "lead_acquisition"
    assert payload["user_id"] == "12345"
    assert payload["force_new_conversation"] is True
    assert payload["message"]["content"] == "Hello"
