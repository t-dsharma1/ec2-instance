from unittest.mock import AsyncMock, patch

from genie_core.utils import logging
from genie_dao.datamodel.chatbot_db_model.models import FlowSupervisorItem, ItemType
from genie_dao.services.flow_supervisor.flow_supervisor_db_service import (  # noqa
    create_flow_supervisor_state,
    get_flow_supervisor_states,
)

_log = logging.get_or_create_logger(logger_name="FlowSupervisorDBService")


mock_flow_supervisor_response = {
    "items": [
        {
            "PK": "test-conversation-uid",
            "SK": "flow_supervisor_state_uid",
            "flow_supervisor_uid": "test_flow_supervisor_uid",
            "flow_supervisor_state_datetime": "2024-05-20T12:00:00",
            "total_unrelated_state_count": 0,
            "consecutive_unrelated_state_count": 0,
            "item_type": "FLOW_SUPERVISOR",
            "item_created_datetime": "2024-05-20T12:00:00",
        }
    ]
}


async def test_create_flow_supervisor_state() -> FlowSupervisorItem:
    mock_client_db = AsyncMock()
    mock_table = AsyncMock()

    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_client_db
    mock_client_db.Table.return_value = mock_table

    with patch("genie_dao.storage.dynamodb.DynamoDBClient", return_value=mock_context_manager):  # noqa
        response = await create_flow_supervisor_state(
            conversation_uid=mock_flow_supervisor_response["items"][0]["PK"],
            total_unrelated_state_count=0,
            consecutive_unrelated_state_count=0,
        )

        assert isinstance(response, FlowSupervisorItem)
        assert response.PK == mock_flow_supervisor_response["items"][0]["PK"]
        assert response.SK.startswith(ItemType.FLOW_SUPERVISOR.value)


async def test_get_flow_supervisor_states() -> list[FlowSupervisorItem]:
    with patch(
        "genie_dao.services.flow_supervisor.flow_supervisor_db_service.query_dynamodb_table",  # noqa
        new_callable=AsyncMock,
    ) as query_dynamodb_table:
        query_dynamodb_table.return_value = mock_flow_supervisor_response

        await get_flow_supervisor_states("mock_conversation_uid")
        query_dynamodb_table.assert_awaited_once()
