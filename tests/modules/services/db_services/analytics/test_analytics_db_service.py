from unittest.mock import AsyncMock, patch

from genie_core.utils import logging
from genie_dao.services.analytics.analytics_db_service import (
    get_conversation_daily_count,
)

_log = logging.get_or_create_logger(logger_name="AnalyticsDBService")


mock_response = {
    "items": [
        {
            "PK": "12345",
            "SK": "CONVERSATION#2024-05-20T12:00:00",
            "conversation_state": "ENDED",
            "conversation_uid": "input123",
            "conversation_start_datetime": "2024-05-20T12:00:00",
            "conversation_end_datetime": "2024-05-20T13:00:00",
            "flow_type": "flow_type",
            "flow_variant_id": "flow_variant_id",
            "user_uid": "user_uid",
            "item_type": "item_type",
            "item_created_datetime": "2024-05-20T12:00:00",
        }
    ]
}


async def test_get_conversation_daily_count_with_ai_states() -> int:
    with (
        patch(
            "genie_dao.services.analytics.analytics_db_service.query_dynamodb_table",
            new_callable=AsyncMock,
        ) as query_dynamodb_table,
        patch(
            "genie_dao.services.analytics.analytics_db_service.get_ai_conversation_states",
            new_callable=AsyncMock,
        ) as get_ai_conversation_state,
    ):
        get_ai_conversation_state.return_value = ["ai_state_1", "ai_state_2", "ai_state_3"]  # noqa: E501
        query_dynamodb_table.return_value = mock_response
        conversations = await get_conversation_daily_count(True)
        query_dynamodb_table.assert_awaited_once()
        assert conversations == len(mock_response["items"])


async def test_get_conversation_daily_count_without_ai_states() -> int:
    with (
        patch(
            "genie_dao.services.analytics.analytics_db_service.query_dynamodb_table",
            new_callable=AsyncMock,
        ) as query_dynamodb_table,
        patch(
            "genie_dao.services.analytics.analytics_db_service.get_ai_conversation_states",
            new_callable=AsyncMock,
        ) as get_ai_conversation_state,
    ):
        get_ai_conversation_state.return_value = []
        query_dynamodb_table.return_value = mock_response
        conversations = await get_conversation_daily_count(True)
        query_dynamodb_table.assert_awaited_once()
        assert conversations == 0
