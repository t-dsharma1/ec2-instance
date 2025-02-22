from datetime import datetime
from typing import Optional

from genie_core.utils import logging
from genie_dao.datamodel.chatbot_db_model import ChatbotTable
from genie_dao.datamodel.chatbot_db_model.models import (
    AIStateItem,
    CustomerContextItem,
    ItemType,
)
from genie_dao.storage.dynamodb import DynamoDBWriter
from genie_dao.storage.operations import query_dynamodb_table

_log = logging.get_or_create_logger(logger_name="AIStateDBService")


@ChatbotTable.inject_writer
async def create_ai_state_for_conversation(
    conversation_uid: str,
    ai_state_name: str,
    ai_state_input_message_uid: str,
    ai_state_output_message_uid: str,
    ai_data_needs: str,
    ai_plan_type: str,
    ai_number_of_lines: str,
    ai_otts: str,
    ai_pin_code: str,
    ai_existing_services: str,
    ai_discussed_plans: str,
    ai_other_needs: str,
    ai_tone: str,
    ai_sentiment: str,
    ai_conversation_summary: str,
    ai_state_type: str,
    writer: DynamoDBWriter,
) -> AIStateItem:
    """Create a new state for the given conversation."""

    ai_state_datetime = datetime.now().isoformat()
    item = {
        "PK": conversation_uid,
        "SK": ItemType.AI_STATE.value + "#" + ai_state_datetime,
        "ai_state_name": ai_state_name,
        "ai_state_datetime": ai_state_datetime,
        "ai_state_input_message_uid": ai_state_input_message_uid,
        "ai_state_output_message_uid": ai_state_output_message_uid,
        "ai_data_needs": ai_data_needs,
        "ai_plan_type": ai_plan_type,
        "ai_number_of_lines": ai_number_of_lines,
        "ai_otts": ai_otts,
        "ai_pin_code": ai_pin_code,
        "ai_existing_services": ai_existing_services,
        "ai_discussed_plans": ai_discussed_plans,
        "ai_other_needs": ai_other_needs,
        "ai_tone": ai_tone,
        "ai_sentiment": ai_sentiment,
        "ai_conversation_summary": ai_conversation_summary,
        "ai_state_type": ai_state_type,
        "item_type": ItemType.AI_STATE.value,
        "item_created_datetime": ai_state_datetime,
    }

    await writer.put_item(Item=item)

    return AIStateItem(**item)


async def get_ai_conversation_states(conversation_uid: str) -> list[AIStateItem]:
    """Retrieve all sorted ai states for a given conversation.

    Parameters:
    - conversation_uid (str): The conversation UID to retrieve states for.

    Returns:
    - A state items for the latest conversation.
    """

    key_condition_expression = "PK = :pk AND begins_with(SK, :sk_prefix)"

    expression_attribute_values = {":pk": conversation_uid, ":sk_prefix": ItemType.AI_STATE.value + "#"}

    # Assuming the query function returns items sorted by sort key in ascending order
    states = (
        await query_dynamodb_table(
            table_name=ChatbotTable.get_table_name(),
            key_condition_expression=key_condition_expression,
            expression_attribute_values=expression_attribute_values,
            consistent_read=True,
        )
    )["items"]

    states.sort(key=lambda x: x["ai_state_datetime"], reverse=True)

    return [AIStateItem(**state) for state in states]


@staticmethod
async def get_conversation_ai_state_by_message_id(conversation_uid: str, message_uid: str) -> list[AIStateItem]:
    """Retrieve AI state for a given conversation based on message_uid.

    Parameters:
    - conversation_uid (str): The conversation UID to retrieve states for.
    - message_uid (str): The message UID to filter the states.

    Returns:
    - A state items for the laterst conversation.
    """

    key_condition_expression = "PK = :pk AND begins_with(SK, :sk_prefix)"

    filter_expression = "ai_state_input_message_uid = :ai_state_input_message_uid"
    expression_attribute_values = {
        ":pk": conversation_uid,
        ":sk_prefix": ItemType.AI_STATE.value + "#",
        ":ai_state_input_message_uid": message_uid,
    }

    # Assuming the query function returns items sorted by sort key in ascending order
    states = (
        await query_dynamodb_table(
            table_name=ChatbotTable.get_table_name(),
            key_condition_expression=key_condition_expression,
            filter_expression=filter_expression,
            expression_attribute_values=expression_attribute_values,
            consistent_read=True,
        )
    )["items"]

    return [AIStateItem(**state) for state in states]


@ChatbotTable.inject_writer
async def create_external_conversation_customer_context(
    conversation_uid: str, customer_context: dict, writer: DynamoDBWriter
) -> CustomerContextItem:
    """Create a new customer context for the given conversation."""

    item = {
        "PK": conversation_uid,
        "SK": ItemType.CUSTOMER_CONTEXT.value,
        "customer_context": customer_context,
        "item_type": ItemType.CUSTOMER_CONTEXT.value,
        "item_created_datetime": datetime.now().isoformat(),
    }

    await writer.put_item(Item=item)

    return CustomerContextItem(**item)


async def get_sorted_external_conversation_customer_context(
    conversation_uid: str,
) -> Optional[CustomerContextItem]:
    """Retrieve latest sorted customer context for a given conversation. The first item
    in the list is the latest customer context.

    Parameters:
    - conversation_uid (str): The conversation UID to retrieve customer context for.

    Returns:
    - A customer context for the conversation.
    """

    key_condition_expression = "PK = :pk AND SK = :sk"

    expression_attribute_values = {":pk": conversation_uid, ":sk": ItemType.CUSTOMER_CONTEXT.value}

    # Assuming the query function returns items sorted by sort key in ascending order
    customer_contexts = (
        await query_dynamodb_table(
            table_name=ChatbotTable.get_table_name(),
            key_condition_expression=key_condition_expression,
            expression_attribute_values=expression_attribute_values,
            consistent_read=True,
        )
    )["items"]
    _log.info(f"Customer Contexts: {customer_contexts}")

    if len(customer_contexts) == 0:
        return None

    customer_contexts.sort(key=lambda x: x["item_created_datetime"], reverse=True)
    customer_contexts_items = [CustomerContextItem(**customer_context) for customer_context in customer_contexts]

    return customer_contexts_items[0]
