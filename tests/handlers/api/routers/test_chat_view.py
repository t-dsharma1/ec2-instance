from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.exceptions import HTTPException
from fastapi_keycloak import FastAPIKeycloak

# Patch the `FastAPIKeycloak` methods before importing the module
with patch.object(FastAPIKeycloak, "__init__", return_value=None), patch(
    "connectai.handlers.utils.api_idp.FastAPIKeycloak._get_admin_token", return_value=None
), patch("connectai.handlers.utils.api_idp.FastAPIKeycloak.open_id_configuration", new_callable=MagicMock), patch(
    "connectai.handlers.utils.api_idp.FastAPIKeycloak.token_uri", new_callable=MagicMock
), patch(
    "connectai.handlers.utils.api_idp.FastAPIKeycloak", new_callable=MagicMock
), patch(
    "connectai.handlers.utils.api_idp", new_callable=MagicMock
), patch(
    "connectai.handlers.utils.api_idp.idp.get_current_user", new_callable=MagicMock
), patch(
    "connectai.handlers.utils.api_idp.FastAPIKeycloak.public_key", new_callable=MagicMock
):
    from connectai.handlers.api.routers import chat_view
    from connectai.modules.datamodel import PagedResponseSchema
    from genie_dao.datamodel.chatbot_db_model.models import (
        ConversationAIStateItem,
        ConversationItem,
    )

mock_new_conversation_response = {
    "items": [
        {
            "PK": "CONVERSATION#123456789",
            "SK": "METADATA#2024-05-20T12:00:00",
            "conversation_state": "ACTIVE",
            "conversation_uid": "mock_conversation_uid",
            "conversation_start_datetime": "2024-05-21T12:00:00",
            "conversation_end_datetime": "2024-05-21T13:00:00",
            "flow_type": "flow_type",
            "flow_variant_id": "flow_variant_id",
            "user_uid": "mock_user_uid",
            "item_type": "item_type",
            "item_created_datetime": "2024-05-21T12:00:00",
        }
    ]
}


@patch("connectai.handlers.api.routers.chat_view.get_conversations", new_callable=AsyncMock)
async def test_get_all_conversations(mock_get_conversations):
    mock_get_conversations.return_value = [
        ConversationItem(**mock_new_conversation_response["items"][0])
    ]  # Your mocked conversations list
    response = await chat_view.get_all_conversations("2021-01-01", page_size=1, page_number=1)
    assert isinstance(response, PagedResponseSchema)
    assert response.results[0].conversation_uid == "mock_conversation_uid"


@patch("connectai.handlers.api.routers.chat_view.get_ai_conversation_states", new_callable=AsyncMock)
@patch("connectai.handlers.api.routers.chat_view.get_conversation_by_pk", new_callable=AsyncMock)
async def test_get_conversation_item_with_no_message_uid(mock_get_conversation_by_pk, mock_get_ai_conversation_states):
    mock_get_conversation_by_pk.return_value = ConversationItem(**mock_new_conversation_response["items"][0])
    mock_get_ai_conversation_states.return_value = ["mock_ai_state"]
    response = await chat_view.get_conversation_item(conversation_uid="mock_conversation_uid", message_uid=None)
    assert isinstance(response, ConversationAIStateItem)
    assert response.conversation_item.conversation_uid == "mock_conversation_uid"
    assert response.ai_state_item == "mock_ai_state"


@patch("connectai.handlers.api.routers.chat_view.get_conversation_ai_state_by_message_id", new_callable=AsyncMock)
@patch("connectai.handlers.api.routers.chat_view.get_conversation_by_pk", new_callable=AsyncMock)
async def test_get_conversation_item_with_message_uid(
    mock_get_conversation_by_pk, mock_get_conversation_ai_state_by_message_id
):
    mock_get_conversation_by_pk.return_value = ConversationItem(**mock_new_conversation_response["items"][0])
    mock_get_conversation_ai_state_by_message_id.return_value = ["mock_ai_state"]
    response = await chat_view.get_conversation_item(
        conversation_uid="mock_conversation_uid", message_uid="mock_message_uid"
    )
    assert isinstance(response, ConversationAIStateItem)
    assert response.conversation_item.conversation_uid == "mock_conversation_uid"
    assert response.ai_state_item == "mock_ai_state"


@patch("connectai.handlers.api.routers.chat_view.get_conversation_by_pk", new_callable=AsyncMock)
async def test_get_conversation_item_with_no_conversation(mock_get_conversation_by_pk):
    mock_get_conversation_by_pk.return_value = None
    with pytest.raises(HTTPException):
        await chat_view.get_conversation_item(conversation_uid="mock_conversation_uid")


@patch("connectai.handlers.api.routers.chat_view.get_conversation_messages", new_callable=AsyncMock)
async def test_get_messages(mock_get_conversation_messages):
    await chat_view.get_messages(conversation_uid="mock_conversation_uid")
    mock_get_conversation_messages.assert_awaited_once_with(conversation_uid="CONVERSATION#mock_conversation_uid")
