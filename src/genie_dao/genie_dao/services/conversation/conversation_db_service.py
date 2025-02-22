import asyncio
import random
import string
from datetime import datetime
from typing import Optional

from genie_core.utils import logging
from genie_dao import pubsub
from genie_dao.datamodel.chatbot_db_model import ChatbotTable
from genie_dao.datamodel.chatbot_db_model.models import ConversationItem, ItemType
from genie_dao.pubsub.chatbot.models import (
    ChatbotConversationEnded,
    ConversationChannel,
)
from genie_dao.services.flow.flow_db_service import (
    get_latest_random_flow_variant_metadata,
)
from genie_dao.services.flow_supervisor.flow_supervisor_db_service import (
    create_flow_supervisor_state,
)
from genie_dao.services.message.message_db_service import get_conversation_messages
from genie_dao.storage.dynamodb import DynamoDBWriter
from genie_dao.storage.operations import query_all_items_dynamodb_table

_log = logging.get_or_create_logger(logger_name="ConversationDBService")


async def ensure_conversation(
    user_uid: str, flow_type: str, conversation_pk: str = None, timeout_time_s: float = 900, renew: bool = False
) -> ConversationItem:
    """Ensures there is a conversation for the given user UID, creating one if necessary
    and timing out if needed.

    Parameters:
    - user_uid (str): The user UID.
    - flow_type (str): The type of conversation to ensure.
    - timeout_time_s (float): The timeout time in seconds.
    - renew (bool): Force a renewal of the conversation.

    Returns:
    - dict: The conversation item.
    """
    exists, conversation = await check_and_get_conversation(
        user_uid=user_uid, flow_type=flow_type, conversation_pk=conversation_pk
    )

    if exists and not renew:
        """Check if the last message sent is more than the timeout time, if so, renew
        the conversation."""
        messages = await get_conversation_messages(conversation_uid=conversation.PK)
        if messages:
            messages.sort(key=lambda x: x.message_sent_datetime)
            time_diff = datetime.fromisoformat(datetime.now().isoformat()) - datetime.fromisoformat(
                messages[-1].item_created_datetime
            )
        else:
            time_diff = datetime.fromisoformat(datetime.now().isoformat()) - datetime.fromisoformat(
                conversation.conversation_start_datetime
            )

        if time_diff.total_seconds() > timeout_time_s:
            _log.warn(
                f"Timeout. Last message sent more than {timeout_time_s} seconds ago ({time_diff.total_seconds()}). Resetting conversation."
            )
            await end_conversation(conversation_uid=conversation.PK)
            flow_data = await get_latest_random_flow_variant_metadata(flow_type)
            flow_variant_id = flow_data.extract_flow_variant_id()
            conversation = await create_conversation(user_uid, flow_type, flow_variant_id)
            await create_flow_supervisor_state(
                conversation_uid=conversation.conversation_uid,
                total_unrelated_state_count=0,
                consecutive_unrelated_state_count=0,
            )

    else:
        _log.info("Instantiating a new conversation")
        flow_data = await get_latest_random_flow_variant_metadata(flow_type)
        flow_variant_id = flow_data.extract_flow_variant_id()
        conversation = await create_conversation(user_uid, flow_type, flow_variant_id)
        await create_flow_supervisor_state(
            conversation_uid=conversation.conversation_uid,
            total_unrelated_state_count=0,
            consecutive_unrelated_state_count=0,
        )

    return conversation


@ChatbotTable.inject_writer
async def create_conversation(
    user_uid: str,
    flow_type: str,
    variant_id: str,
    writer: DynamoDBWriter,
) -> ConversationItem:
    """Create a new conversation for the given user UID.

    There are 2 items created for each conversation:
    1. The metadata item with the conversation details. - PK: conversation_uid, SK: metadata
    2. The partition by hour item with the conversation details. - PK: partition_date_hour, SK: conversation_uid
    Timestamp item is required for optimized querying of conversations by specific hour.

    Parameters:
    - user_uid (str): The user UID for whom to create the conversation.
    - flow_type (str): The type of conversation to create.
    - variant_id (str): The variant ID of the conversation.

    Returns:
    - dict: The created conversation item.
    """

    conversation_timestamp = datetime.now()

    # Create the conversation metadata item
    conversation_start_datetime = conversation_timestamp.isoformat()
    # Generate a unique conversation UID here (e.g., using UUID)

    conversation_uid = (
        ItemType.CONVERSATION.value + "#" + "".join(random.choices(string.ascii_uppercase + string.digits, k=16))
    )
    item = {
        "PK": conversation_uid,
        "SK": ItemType.METADATA.value + "#" + conversation_start_datetime,
        "flow_type": flow_type,
        "flow_variant_id": variant_id,
        "conversation_uid": conversation_uid,
        "conversation_state": "ACTIVE",
        "conversation_start_datetime": conversation_start_datetime,
        "conversation_end_datetime": "",
        "user_uid": user_uid,
        "item_type": ItemType.CONVERSATION.value,
        "item_created_datetime": conversation_start_datetime,
    }

    await writer.put_item(Item=item)

    # Create a partition by hour item for the conversation
    partition_date_hour = conversation_timestamp.strftime("%Y-%m-%d %H")

    conversation_partition_item = {**item}
    conversation_partition_item["PK"] = partition_date_hour
    conversation_partition_item["SK"] = conversation_uid
    conversation_partition_item["item_type"] = ItemType.CONVERSATION_BY_DATE.value

    await writer.put_item(Item=conversation_partition_item)

    return ConversationItem(**item)


async def check_and_get_conversation(
    user_uid: str, flow_type: str, conversation_pk: str = None
) -> tuple[bool, ConversationItem | None]:
    """Check if there's a conversation for the given user UID and for given type and
    retrieve it if exists. The key condition expression to query the table consists of
    the user UID and the SK with the metadata prefix, to make sure we only get the
    metadata items and not the conversations by date partition.

    :param str user_uid: The user UID to check for conversations.
    :param str flow_type: The type of conversation to check for.
    :param str conversation_pk: If specified we enforce that returned conversation is
        not the first active encountered but this exact one
    :return: A tuple where the first element is a boolean indicating if a conversation
        exists, and the second element is the conversation item if it exists.
    :rtype: Tuple[bool, ConversationItem | None]:
    """
    # Assume 'conversations_by_user' is the GSI to query conversations by user UID
    index_name = "UserConversationsIndex"

    pk_prefix = ItemType.CONVERSATION.value
    if conversation_pk is not None:
        pk_prefix = conversation_pk

    key_condition_expression = "user_uid = :user_uid AND begins_with(SK, :sk_prefix)"
    filter_expression = "begins_with(PK, :pk_prefix) and flow_type = :flow_type"
    expression_attribute_values = {
        ":pk_prefix": pk_prefix,
        ":sk_prefix": ItemType.METADATA.value,
        ":user_uid": user_uid,
        ":flow_type": flow_type,
    }

    conversations = await query_all_items_dynamodb_table(
        table_name=ChatbotTable.get_table_name(),
        index_name=index_name,
        filter_expression=filter_expression,
        key_condition_expression=key_condition_expression,
        expression_attribute_values=expression_attribute_values,
    )

    if conversations:
        conversations.sort(key=lambda x: x["item_created_datetime"], reverse=True)
        if len(conversations) > 1:
            _log.info(f"ERROR: Multiple active conversations for flow `{flow_type}` for user `{user_uid}`")
            _log.info(f"Conversations: {conversations}")
        if conversations[0]["conversation_state"] == "ACTIVE":
            _log.info(f"Found active conversation for flow `{flow_type}` for user `{user_uid}`")
            return True, ConversationItem(**conversations[0])
    _log.info(f"No active conversation for flow `{flow_type}` for user `{user_uid}`")
    return False, None


@ChatbotTable.inject_writer
async def end_conversation(
    conversation_uid: str,
    writer: DynamoDBWriter,
) -> Optional[ConversationItem]:
    """End the conversation by updating the conversation state."""

    conversation_end_time: str = datetime.now().isoformat()
    existing_conv = await get_conversation_by_pk(conversation_uid=conversation_uid)
    if existing_conv is None:
        return None

    item = {
        "PK": conversation_uid,
        "SK": ItemType.METADATA.value + "#" + conversation_end_time,
        "conversation_state": "ENDED",
        "conversation_uid": conversation_uid,
        "conversation_start_datetime": existing_conv.conversation_start_datetime,
        "conversation_end_datetime": conversation_end_time,
        "flow_type": existing_conv.flow_type,
        "flow_variant_id": existing_conv.flow_variant_id,
        "user_uid": existing_conv.user_uid,
        "item_type": ItemType.CONVERSATION.value,
        "item_created_datetime": conversation_end_time,
    }

    async def on_commit():
        pubsub.publish(ConversationChannel(conversation_pk=conversation_uid), ChatbotConversationEnded())

    writer.register_on_commit_hook(on_commit)
    await writer.put_item(Item=item)
    return ConversationItem(**item)


async def get_conversation_by_pk(conversation_uid: str) -> Optional[ConversationItem]:
    """Retrieve a conversation by its primary key.

    Parameters:
    - conversation_uid (str): The conversation UID

    Returns:
    - ConversationItem: A conversation item.
    """
    key_condition_expression = "PK = :pk AND begins_with(SK, :sk_prefix)"

    filter_expression = "item_type = :item_type"

    expression_attribute_values = {
        ":pk": conversation_uid,
        ":sk_prefix": ItemType.METADATA.value + "#",
        ":item_type": ItemType.CONVERSATION.value,
    }

    conversations = await query_all_items_dynamodb_table(
        table_name=ChatbotTable.get_table_name(),
        filter_expression=filter_expression,
        key_condition_expression=key_condition_expression,
        expression_attribute_values=expression_attribute_values,
    )

    if len(conversations) == 0:
        return None

    conversations.sort(key=lambda x: x["item_created_datetime"], reverse=True)

    return ConversationItem(**conversations[0])


async def get_conversations(partition_date: str) -> list[ConversationItem]:
    """Retrieve conversations based on partition date for all 24 hours.

    Parameters:
    - partition_date (str): The partition date to retrieve conversations for.

    Returns:
    - list: A list of conversation items.
    """
    key_condition_expression = "PK = :pk"

    semaphore = asyncio.Semaphore(24)
    results = [None] * 24
    tasks = []

    async def run_partition_by_hour(index, partition_date):
        expression_attribute_values = {":pk": partition_date}
        async with semaphore:
            try:
                conversations = await query_all_items_dynamodb_table(
                    table_name=ChatbotTable.get_table_name(),
                    key_condition_expression=key_condition_expression,
                    expression_attribute_values=expression_attribute_values,
                )
                results[index] = conversations
            except Exception as e:
                results[index] = []
                _log.error(f"Error fetching conversations for partition date of hour {partition_date}: {e}")

    # Fetch all conversations for the given partition date for all 24 hours
    for i in range(24):
        task = run_partition_by_hour(i, partition_date + f" {i:02d}")
        tasks.append(task)

    await asyncio.gather(*tasks)

    # Flatten the results
    results = [item for sublist in results for item in sublist]

    return [ConversationItem(**c) for c in results]
