from typing import Callable, Optional

from connectai.handlers.internal_bus.shared_pubsub import (
    PublicPubSub,
    PubSubKey,
    PubSubKeyType,
    PubSubPublisherType,
)
from connectai.modules.datamodel import AgentResponsePayload, OutputMessage


class ConversationSessionBus:
    def __init__(self, shared_pubsub: PublicPubSub) -> None:
        """Initializes an in-memory shared application bus that holds:
        - Async PubSub hub
        - Conversation Context
        """
        self.shared_pubsub: PublicPubSub = shared_pubsub
        self.conversation_id: Optional[str] = None

    def set_conversation_id(self, conversation_id: str) -> None:
        """Set the conversation ID."""
        self.conversation_id = conversation_id

    def subscribe_to_llm_chunk_response(
        self,
        subscriber_id: str,
        callback: Callable,
    ) -> None:
        """Subscribe to the LLM chunk response topic.

        Args:
            subscriber_id (str): The unique ID of the subscriber.
            callback (Callable): The callback function to be executed when a message is received
        """
        self.shared_pubsub.subscribe(
            subscriber_id=subscriber_id,
            publisher_type=PubSubPublisherType.LLM,
            key=PubSubKey.RESPONSE,
            key_type=PubSubKeyType.CHUNK,
            callback=callback,
        )

    def subscribe_to_response_completed(
        self,
        subscriber_id: str,
        callback: Callable,
    ) -> None:
        """Subscribe to the LLM chunk response topic.

        Args:
            subscriber_id (str): The unique ID of the subscriber.
            callback (Callable): The callback function to be executed when a message is received
        """
        self.shared_pubsub.subscribe(
            subscriber_id=subscriber_id,
            publisher_type=PubSubPublisherType.LLM,
            key=PubSubKey.RESPONSE_COMPLETED,
            key_type=PubSubKeyType.GENERIC,
            callback=callback,
        )

    def publish_chunk(
        self,
        message_content: str,
    ) -> None:
        """Publish a pubsub chunk message to the LLM topic.

        Args:
            message_content (str): The message content to be published
        """
        self.shared_pubsub.publish(
            publisher_type=PubSubPublisherType.LLM,
            key=PubSubKey.RESPONSE,
            key_type=PubSubKeyType.CHUNK,
            message=AgentResponsePayload(
                response_completed=False,
                message=OutputMessage(content=message_content),
                conversation_id=self.conversation_id,
            ),
        )

    async def publish_response_completed(self, conversation_ended_flag=False) -> None:
        self.shared_pubsub.publish(
            publisher_type=PubSubPublisherType.LLM,
            key=PubSubKey.RESPONSE_COMPLETED,
            key_type=PubSubKeyType.OTHER,
            message=AgentResponsePayload(
                response_completed=True,
                conversation_ended_flag=conversation_ended_flag,
                conversation_id=self.conversation_id,
            ),
        )

    async def clear_all_listeners(self) -> None:
        """Clear all listeners."""
        await self.shared_pubsub.clear_async_listeners()
