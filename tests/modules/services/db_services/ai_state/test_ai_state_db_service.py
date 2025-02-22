from unittest.mock import AsyncMock, patch

from connectai.settings import GLOBAL_SETTINGS
from genie_core.utils import logging
from genie_dao.datamodel.chatbot_db_model.models import AIStateItem, ItemType
from genie_dao.services.ai_state import (
    create_ai_state_for_conversation,
    get_ai_conversation_states,
    get_conversation_ai_state_by_message_id,
)

_log = logging.get_or_create_logger(logger_name="AIStateDBService")


mock_response = {
    "items": [
        {
            "PK": "12345",
            "SK": "AI_STATE#2024-05-20T12:00:00",
            "ai_state_name": "ai_state",
            "ai_state_datetime": "2024-05-20T12:00:00",
            "ai_state_input_message_uid": "input123",
            "ai_state_output_message_uid": "output123",
            "ai_data_needs": "needs",
            "ai_plan_type": "plan_type",
            "ai_number_of_lines": "5",
            "ai_otts": "otts",
            "ai_pin_code": "pin",
            "ai_existing_services": "services",
            "ai_discussed_plans": "plans",
            "ai_other_needs": "other_needs",
            "ai_tone": "tone",
            "ai_sentiment": "sentiment",
            "ai_conversation_summary": "summary",
            "ai_state_type": "state_type",
            "item_type": "item_type",
            "item_created_datetime": "2024-05-20T12:00:00",
        }
    ]
}


async def test_create_ai_state_for_conversation():
    mock_client_db = AsyncMock()
    mock_table = AsyncMock()

    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_client_db
    mock_client_db.Table.return_value = mock_table

    with patch("genie_dao.storage.dynamodb.DynamoDBClient", return_value=mock_context_manager):  # noqa
        conversation_uid = "test-conversation-uid"
        ai_state_name = "test-ai-state-name"
        ai_state_input_message_uid = "input-uid"
        ai_state_output_message_uid = "output-uid"
        ai_data_needs = "data-needs"
        ai_plan_type = "plan-type"
        ai_number_of_lines = "number-of-lines"
        ai_otts = "otts"
        ai_pin_code = "pin-code"
        ai_existing_services = "existing-services"
        ai_discussed_plans = "discussed-plans"
        ai_other_needs = "other-needs"
        ai_tone = "tone"
        ai_sentiment = "sentiment"
        ai_conversation_summary = "conversation-summary"
        ai_state_type = "state-type"

        result = await create_ai_state_for_conversation(
            conversation_uid,
            ai_state_name,
            ai_state_input_message_uid,
            ai_state_output_message_uid,
            ai_data_needs,
            ai_plan_type,
            ai_number_of_lines,
            ai_otts,
            ai_pin_code,
            ai_existing_services,
            ai_discussed_plans,
            ai_other_needs,
            ai_tone,
            ai_sentiment,
            ai_conversation_summary,
            ai_state_type,
        )

        mock_client_db.Table.assert_awaited_once_with(GLOBAL_SETTINGS.environment.value.lower() + "_" + "chatbot_table")
        mock_table.put_item.assert_awaited()

        assert isinstance(result, AIStateItem)
        assert result.PK == conversation_uid
        assert result.SK.startswith(ItemType.AI_STATE.value)
        assert result.ai_state_name == ai_state_name


async def test_get_ai_conversation_states():
    with patch(
        "genie_dao.services.ai_state.ai_state_db_service.query_dynamodb_table",  # noqa
        new_callable=AsyncMock,
    ) as query_dynamodb_table:
        query_dynamodb_table.return_value = mock_response

        await get_ai_conversation_states("mock_conversation_uid")
        query_dynamodb_table.assert_awaited_once()


async def test_get_conversation_ai_state_by_message_id():
    with patch(
        "genie_dao.services.ai_state.ai_state_db_service.query_dynamodb_table",
        new_callable=AsyncMock,
    ) as query_dynamodb_table:
        query_dynamodb_table.return_value = mock_response
        conversation_uid = "mock_conversation_uid"
        message_id = "mock_message_uid"
        result = await get_conversation_ai_state_by_message_id(conversation_uid, message_id)  # noqa: E501
        query_dynamodb_table.assert_awaited_once()
        assert result[0].PK == mock_response["items"][0]["PK"]
        assert result[0].SK.startswith(ItemType.AI_STATE.value)
