from datetime import datetime

from genie_core.utils import logging
from genie_dao.datamodel.chatbot_db_model import ChatbotTable
from genie_dao.datamodel.chatbot_db_model.models import FlowSupervisorItem, ItemType
from genie_dao.storage.dynamodb import DynamoDBWriter
from genie_dao.storage.operations import query_dynamodb_table

_log = logging.get_or_create_logger(logger_name="FlowSupervisorDBService")


@ChatbotTable.inject_writer
async def create_flow_supervisor_state(
    conversation_uid: str,
    total_unrelated_state_count: int,
    consecutive_unrelated_state_count: int,
    writer: DynamoDBWriter,
) -> FlowSupervisorItem:
    """Create a new flow supervisor item within a conversation.

    Parameters:
    - conversation_uid (str): The conversation UID.
    - unrelated_state_count (int): The number of unrelated states.

    Returns:
    - dict: The created message item.
    """

    flow_supervisor_state_datetime: str = datetime.now().isoformat()
    flow_supervisor_state_uid = ItemType.FLOW_SUPERVISOR.value + "#" + "".join(flow_supervisor_state_datetime)

    item = {
        "PK": conversation_uid,
        "SK": flow_supervisor_state_uid,
        "flow_supervisor_uid": flow_supervisor_state_uid,
        "flow_supervisor_state_datetime": flow_supervisor_state_datetime,
        "total_unrelated_state_count": total_unrelated_state_count,
        "consecutive_unrelated_state_count": consecutive_unrelated_state_count,
        "item_type": ItemType.FLOW_SUPERVISOR.value,
        "item_created_datetime": flow_supervisor_state_datetime,
    }
    await writer.put_item(Item=item)

    return FlowSupervisorItem(**item)


async def get_flow_supervisor_states(conversation_uid: str) -> list[FlowSupervisorItem]:
    """Retrieve the latest flow supervisor state for a given conversation."""
    key_condition_expression = "PK = :pk AND begins_with(SK, :sk_prefix)"

    expression_attribute_values = {":pk": conversation_uid, ":sk_prefix": ItemType.FLOW_SUPERVISOR.value + "#"}

    # Assuming the query function returns items sorted by sort key in ascending order
    flow_supervisor_states = (
        await query_dynamodb_table(
            table_name=ChatbotTable.get_table_name(),
            key_condition_expression=key_condition_expression,
            expression_attribute_values=expression_attribute_values,
            consistent_read=True,
        )
    )["items"]

    flow_supervisor_states.sort(key=lambda x: x["flow_supervisor_state_datetime"], reverse=True)

    return [FlowSupervisorItem(**flow_supervisor_state) for flow_supervisor_state in flow_supervisor_states]
