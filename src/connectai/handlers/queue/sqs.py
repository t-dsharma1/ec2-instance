import dataclasses
import datetime
import threading
import time
from typing import Any, Callable

import boto3

from connectai.handlers import get_or_create_logger
from connectai.modules.datamodel import WorkQueueItem
from connectai.settings import GLOBAL_SETTINGS
from genie_core.utils.decorators import cache_results

_log = get_or_create_logger(logger_name="QueueSQS")


class SQSQueue:
    """SQS queue management class.

    Takes care of queue creation, listing, and URL retrieval.
    """

    def __init__(self, reference_queue_name: str):
        self.queue_name = reference_queue_name
        self.queue_name = self._format_queue_name(reference_queue_name)
        self._client = boto3.client("sqs", region_name=GLOBAL_SETTINGS.aws_region)

    def _format_queue_name(self, queue_name: str) -> str:
        """Format the queue name to be used in the SQS."""
        _log.debug(f"Queue name before formatting: {queue_name}")
        queue_name = queue_name.replace("-", "_")
        queue_name = queue_name.replace(".", "_")
        queue_name = queue_name.replace("_fifo", ".fifo")
        _log.debug(f"Queue name after formatting: {queue_name}")
        return queue_name

    def bootstrap(self):
        """Set up and configure the queue on startup."""
        queue_urls = self.list_queues()
        queue_url = next((url for url in queue_urls if self.queue_name in url), None)

        if queue_url is None:
            queue_url = self.create_queue()

        _log.info(f"Queue URL: {queue_url}")

    @cache_results(expiration_seconds=600)
    def get_queue_url(self) -> str:
        """Retrieve the URL for the queue by querying SQS.

        Cache this value in production to minimize API calls.
        """
        response = self._client.get_queue_url(QueueName=self.queue_name)
        return response["QueueUrl"]

    def create_queue(self) -> str:
        """Create a new SQS FIFO queue if it does not exist."""
        attributes = {
            "DelaySeconds": "0",
            "MaximumMessageSize": "4096",  # Set to 4 KiB
            "MessageRetentionPeriod": "345600",  # Default: 4 days
            "ReceiveMessageWaitTimeSeconds": "0",  # Immediate return
            "VisibilityTimeout": "60",  # 60 seconds
            "FifoQueue": "true",  # FIFO queue
            "ContentBasedDeduplication": "true",  # Enable deduplication
        }
        response = self._client.create_queue(QueueName=self.queue_name, Attributes=attributes)
        _log.info(f"Created new queue at URL: {response['QueueUrl']}")
        return response["QueueUrl"]

    def list_queues(self) -> list:
        """List all queues in the SQS."""
        response = self._client.list_queues()
        queue_urls = response.get("QueueUrls", [])
        return queue_urls

    @cache_results(expiration_seconds=600)
    def get_client(self) -> Any:
        """Instantiate and return the SQS client."""
        if self._client is None:
            self._client = boto3.client(
                "sqs",
                region_name=self.region_name,
            )
        return self._client


class SQSQueuePublisher:
    """Queue publisher class to handle bootstraping and pushing items to the queue."""

    def __init__(self, reference_queue_name: str):
        """Initialize the queue and bootstrap it."""
        self.queue = SQSQueue(reference_queue_name=reference_queue_name)
        self.bootstrap_queue()
        self.queue_url = self.queue.get_queue_url()

    def bootstrap_queue(self):
        """Bootstrap the queue on startup."""
        self.queue.bootstrap()

    def push(self, item: WorkQueueItem):
        """Push a new item to the queue."""
        queue_url = self.queue_url
        response = self.queue._client.send_message(
            QueueUrl=queue_url,
            MessageBody=str(item.to_json()),  # Assuming WorkQueueItem has a to_dict method
            # MessageGroupId="Chatbot_data",  # Necessary for FIFO queues
            MessageGroupId=datetime.datetime.now().isoformat(),  # TODO: Group Messages by user instead of using timestamp
        )
        _log.debug(f"Message sent with ID: {response['MessageId']}")


@dataclasses.dataclass
class SQSMessageHandler:
    """SQS message handler class.

    Takes care of processing messages from the queue.
    """

    process_message_callback: Callable[[dict], None]

    def process_message(self, message: dict) -> None:
        """Process the message using the provided callback."""
        self.process_message_callback(message)


class SQSQueueListener:
    """SQS queue listener class.

    Listens for messages on the queue and processes them.
    """

    thread: threading.Thread

    def __init__(
        self,
        message_handler: SQSMessageHandler,
        reference_queue_name: str,
        thread_wait_time_seconds: float = 0.5,
        polling_wait_time: float = 1,
        max_number_of_messages: int = 1,
    ):
        self.thread = threading.Thread(target=self.listen)
        self.message_handler = message_handler
        self.sqs_client: SQSQueue = SQSQueue(reference_queue_name=reference_queue_name)
        self.boto_client = self.sqs_client.get_client()
        self.wait_time_seconds = thread_wait_time_seconds
        self.max_number_of_messages = max_number_of_messages
        self.polling_wait_time = polling_wait_time

    def start_listening(self) -> None:
        self.thread.start()
        _log.info(f"Started SQS listener with id: {self.thread.native_id}")

    def listen(self) -> None:
        """Start listening for messages on the queue."""
        _log.info(f"Starting listener for queue: {self.sqs_client}")
        while True:
            _log.debug("Polling for messages ...")
            messages = self.boto_client.receive_message(
                QueueUrl=self.sqs_client.get_queue_url(),
                WaitTimeSeconds=self.polling_wait_time,  # Polling wait time
                MaxNumberOfMessages=self.max_number_of_messages,  # Maximum number of messages to receive
            )
            if "Messages" in messages:
                for message in messages["Messages"]:
                    _log.debug(f"Received and Processing message: {message}")
                    try:
                        self.message_handler.process_message(message)
                        _log.debug("Finished processing message, attempting to delete message from queue")

                        for attempt in range(3):
                            try:
                                self.boto_client.delete_message(
                                    QueueUrl=self.sqs_client.get_queue_url(), ReceiptHandle=message["ReceiptHandle"]
                                )
                                _log.debug("Message successfully deleted from queue")
                                break
                            except Exception as e:
                                _log.warning(f"Attempt {attempt + 1} failed to delete message. Error: {e}")

                        else:  # Executed after the loop completes without a break
                            _log.error("Failed to delete message after 3 attempts.")

                    except Exception as e:
                        _log.error(f"Error processing message: {e}")

            time.sleep(self.wait_time_seconds)
