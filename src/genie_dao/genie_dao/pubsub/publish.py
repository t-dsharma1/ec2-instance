import asyncio
import os

from ably import AblyRest
from ably.types.message import Message

from genie_dao.pubsub import models as pubsub_models


async def __do_publish(channel_name: str, ably_message: Message):
    ably_client = AblyRest(os.getenv("ABLY_API_KEY"))
    ably_channel = ably_client.channels.get(channel_name)
    await ably_channel.publish(ably_message)


def publish(channel: pubsub_models.BaseChannel, message: pubsub_models.BaseMessage):
    ably_message = Message(**message.model_dump())

    loop = asyncio.get_event_loop()
    loop.create_task(__do_publish(str(channel), ably_message))
