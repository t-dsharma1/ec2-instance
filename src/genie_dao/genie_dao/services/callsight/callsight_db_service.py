from datetime import datetime

from genie_core.utils import logging
from genie_dao import pubsub
from genie_dao.datamodel.chatbot_db_model.chatbot_db_table import ChatbotTable
from genie_dao.datamodel.chatbot_db_model.models import CallsightItem, ItemType
from genie_dao.pubsub.chatbot.models import (
    ChatbotPostConversationJobsFinished,
    ConversationChannel,
)
from genie_dao.services.flow.flow_db_service import get_latest_flow_variants_metadata
from genie_dao.storage.dynamodb import DynamoDBWriter
from genie_dao.storage.operations import query_dynamodb_table

_log = logging.get_or_create_logger(logger_name="CallsightDBService")


@ChatbotTable.inject_writer
async def create_callsight_response_for_conversation(
    conversation_uid: str,
    callsight_str_response: str,
    writer: DynamoDBWriter,
) -> CallsightItem:
    """Create a new callsight response for the given conversation in the db."""

    callsight_datetime = datetime.now().isoformat()
    item = {
        "PK": conversation_uid,
        "SK": ItemType.CALLSIGHT.value + "#" + callsight_datetime,
        "callsight_str_response": callsight_str_response,
        "item_type": ItemType.CALLSIGHT.value,
        "item_created_datetime": callsight_datetime,
    }

    async def on_commit():
        pubsub.publish(
            ConversationChannel(conversation_pk=conversation_uid),
            ChatbotPostConversationJobsFinished(data=CallsightItem(**item)),
        )

    writer.register_on_commit_hook(on_commit)
    await writer.put_item(Item=item)
    return CallsightItem(**item)


async def get_callsight_responses_for_conversation(conversation_pk: str) -> list[CallsightItem]:
    """Retrieve all time-sorted callsight responses for a given conversation.

    Parameters:
    - conversation_uid (str): The conversation UID to retrieve states for.

    Returns:
    - list[CallsightItem]: The list of callsight responses for the given conversation.
    """

    table_name = ChatbotTable.get_table_name()

    key_condition_expression = "PK = :pk AND begins_with(SK, :sk_prefix)"

    expression_attribute_values = {":pk": conversation_pk, ":sk_prefix": ItemType.CALLSIGHT.value + "#"}

    # Assuming the query function returns items sorted by sort key in ascending order
    callsight_responses = (
        await query_dynamodb_table(
            table_name=table_name,
            key_condition_expression=key_condition_expression,
            expression_attribute_values=expression_attribute_values,
            consistent_read=True,
        )
    )["items"]

    callsight_responses.sort(key=lambda x: x["item_created_datetime"], reverse=True)

    return [CallsightItem(**response) for response in callsight_responses]


async def get_latest_callsight_pipeline(flow_id: str) -> dict:
    """Fetch the latest callsight pipeline in the base flow variant for the given
    flow_id.

    Parameters:
    - flow_id (str): Id of the flow
    Returns:
    - dict: The callsight pipeline
    """

    return (await get_latest_flow_variants_metadata(flow_id=flow_id))[0].callsight_pipeline
