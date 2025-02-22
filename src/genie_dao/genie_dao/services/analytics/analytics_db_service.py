from datetime import datetime, timedelta

from genie_core.utils import logging
from genie_dao.datamodel.chatbot_db_model import ChatbotTable
from genie_dao.datamodel.chatbot_db_model.models import ItemType
from genie_dao.services import get_ai_conversation_states
from genie_dao.storage.operations import query_dynamodb_table

_log = logging.get_or_create_logger(logger_name="AnalyticsDBService")


async def get_conversation_daily_count(today: bool) -> int:
    """Retrieve the number of conversations for current day or previous day.

    Parameters:
    - today (bool): Whether to get the count for today or yesterday.

    Returns:
    - int: The number of conversations for the given day.
    """
    index_name = "ItemTypeIndex"

    # Query all items where ItemType = 'Conversation' with datetime
    conversations = (
        await query_dynamodb_table(
            table_name=ChatbotTable.get_table_name(),
            index_name=index_name,
            key_condition_expression="item_type = :itemType",
            filter_expression="conversation_start_datetime BETWEEN :conversation_start_datetime_lt AND :conversation_start_datetime_gt",
            expression_attribute_values={
                ":itemType": ItemType.CONVERSATION.value,
                ":conversation_start_datetime_lt": (datetime.now() - timedelta(days=0 if today else 1)).strftime(
                    "%Y-%m-%dT00:00:00.000000"
                ),
                ":conversation_start_datetime_gt": (datetime.now() - timedelta(days=0 if today else 1)).strftime(
                    "%Y-%m-%dT23:59:59.999999"
                ),
            },
        )
    )["items"]

    conversation_count = 0
    for conversation in conversations:
        ai_state_item_list = await get_ai_conversation_states(conversation_uid=conversation["PK"])
        if len(ai_state_item_list) > 0:
            conversation_count += 1

    return conversation_count
