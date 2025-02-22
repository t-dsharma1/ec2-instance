import datetime
from unittest.mock import MagicMock, patch

import pytest

from connectai.handlers.queue.sqs import (
    SQSMessageHandler,
    SQSQueue,
    SQSQueueListener,
    SQSQueuePublisher,
)
from connectai.modules.datamodel import WorkQueueItem


@pytest.fixture
def mock_boto_client():
    with patch("boto3.client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_threading_client():
    with patch("threading.Thread") as mock_client:
        yield mock_client


@pytest.fixture
def queue_name():
    return "test-queue.fifo"


@pytest.fixture
def sqs_queue(mock_boto_client, queue_name):
    mock_client_instance = mock_boto_client.return_value
    mock_client_instance.create_queue.return_value = {
        "QueueUrl": f"https://sqs.us-east-1.amazonaws.com/123456789012/{queue_name}"
    }
    mock_client_instance.get_queue_url.return_value = {
        "QueueUrl": f"https://sqs.us-east-1.amazonaws.com/123456789012/{queue_name}"
    }
    mock_client_instance.list_queues.return_value = {
        "QueueUrls": [f"https://sqs.us-east-1.amazonaws.com/123456789012/{queue_name}"]
    }
    return SQSQueue(queue_name)


def test_bootstrap_queue(sqs_queue):
    sqs_queue.bootstrap()
    assert sqs_queue.get_queue_url() is not None


def test_create_queue(sqs_queue):
    queue_url = sqs_queue.create_queue()
    assert queue_url is not None


def test_list_queues(sqs_queue):
    queues = sqs_queue.list_queues()
    assert len(queues) > 0


def test_get_queue_url(sqs_queue):
    queue_url = sqs_queue.get_queue_url()
    assert queue_url is not None


@patch.object(SQSQueue, "get_queue_url")
def test_push_message(mock_get_queue_url, sqs_queue):
    mock_get_queue_url.return_value = sqs_queue.get_queue_url()
    publisher = SQSQueuePublisher(sqs_queue.queue_name)
    item = WorkQueueItem(
        chat_message="Test message",
        chat_timestamp=datetime.datetime.now(),
        from_number="1234567890",
        to_number="0987654321",
        business_id="business123",
        session_id="session123",
        source="test_source",
    )
    publisher.push(item)
    assert publisher.queue_url is not None


def test_message_handler():
    mock_callback = MagicMock()
    handler = SQSMessageHandler(process_message_callback=mock_callback)
    message = {"body": "test"}
    handler.process_message(message)
    mock_callback.assert_called_once_with(message)


@patch.object(SQSQueue, "get_queue_url")
def test_listener_start(mock_get_queue_url, sqs_queue, mock_threading_client):
    mock_get_queue_url.return_value = sqs_queue.get_queue_url()
    mock_handler = MagicMock()
    message_handler = SQSMessageHandler(process_message_callback=mock_handler)
    listener = SQSQueueListener(message_handler, sqs_queue.queue_name, thread_wait_time_seconds=0.1)
    listener.start_listening()
    assert listener.thread.is_alive()
    listener.thread.join(timeout=1)  # Allow the thread to start properly


@patch.object(SQSQueue, "get_queue_url")
@patch.object(SQSQueueListener, "listen")
def test_listener_listen(mock_listen, mock_get_queue_url, sqs_queue):
    mock_get_queue_url.return_value = sqs_queue.get_queue_url()
    mock_handler = MagicMock()
    message_handler = SQSMessageHandler(process_message_callback=mock_handler)
    listener = SQSQueueListener(message_handler, sqs_queue.queue_name, thread_wait_time_seconds=0.1)
    listener.listen()
    mock_listen.assert_called_once()


def test_create_queue_exception(sqs_queue):
    with patch.object(sqs_queue._client, "create_queue", side_effect=Exception("Error")):
        with pytest.raises(Exception):
            sqs_queue.create_queue()
