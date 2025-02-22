from copy import deepcopy
from unittest.mock import AsyncMock, patch

import pytest

from connectai.settings import GLOBAL_SETTINGS
from genie_dao.datamodel.chatbot_db_model.models import (
    ConversationItem,
    Flow,
    FlowCallSightConfig,
    FlowStateMachine,
    FlowStateMachineConfig,
    FlowStateMachineFlowSupervisor,
    FlowStateMachineState,
    FlowSupervisorItem,
    ItemType,
    MessageItem,
    VariantConfig,
)
from genie_dao.services.conversation.conversation_db_service import (  # noqa: E501
    check_and_get_conversation,
    create_conversation,
    end_conversation,
    ensure_conversation,
    get_conversation_by_pk,
    get_conversations,
)

mock_response = {
    "items": [
        {
            "PK": "CONVERSATION#97869P21HG7OTRFW",
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

mock_response_multiple_conversations = {
    "items": [
        {
            "PK": "CONVERSATION#1111P21HG89IUYJ",
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
        },
        {
            "PK": "CONVERSATION#97869P21HG7OTRFW",
            "SK": "METADATA#2024-05-20T10:00:00",
            "conversation_state": "ACTIVE",
            "conversation_uid": "mock_conversation_uid",
            "conversation_start_datetime": "2024-05-20T12:00:00",
            "conversation_end_datetime": "2024-05-20T13:00:00",
            "flow_type": "flow_type",
            "flow_variant_id": "flow_variant_id",
            "user_uid": "mock_user_uid",
            "item_type": "item_type",
            "item_created_datetime": "2024-05-20T12:00:00",
        },
    ]
}


mock_null_response = []

mocked_flow_state_machine = FlowStateMachine(
    FlowConfig=FlowStateMachineConfig(
        is_ai_first_message=True,
        translation_service_enabled=True,
        variants_config=VariantConfig(variants_weights=[1, 2]),
        flow_supervisor=FlowStateMachineFlowSupervisor(),
        callsight=FlowCallSightConfig(enabled=False),
    ),
    FlowStates={"mock_flow_states": FlowStateMachineState(next_states=["mock_states"])},
)

mock_flow_response = {
    "PK": "CONVERSATION#97869P21HG7OTRFW",
    "SK": "METADATA#2024-05-20T10:00:00",
    "flow_states": {},
    "flow_state_machine": mocked_flow_state_machine,
    "flow_context_map": {},
    "flow_base_config": "flow_base_config",
    "flow_config_llm_prompts": {},
    "flow_utility_prompts": {},
    "flow_display_name": "",
    "flow_description": "",
    "item_type": "item_type",
    "item_created_datetime": "2024-05-20T12:00:00",
    "item_deleted_datetime": None,
    "channel": None,
    "product_segment": None,
    "experience_type": None,
}


mock_flow_supervisor_response = {
    "PK": "CONVERSATION#97869P21HG7OTRFW",
    "SK": "FLOW_SUPERVISOR#2024-05-20T10:00:00",
    "flow_supervisor_uid": "flow_supervisor_uid",
    "flow_supervisor_state_datetime": "2024-05-20T12:00:00",
    "total_unrelated_state_count": 0,
    "consecutive_unrelated_state_count": 0,
    "item_type": "item_type",
    "item_created_datetime": "2024-05-20T12:00:00",
}

mock_messages_response = {
    "items": [
        {
            "PK": "CONVERSATION#97869P21HG7OTRFW",
            "SK": "MESSAGE#2024-05-20T10:00:00",
            "message_uid": "message_uid",
            "message_sent_datetime": "2024-05-20T10:00:00",
            "message_type": "INPUT",
            "message_content": "raw_message_content",
            "message_content_en": "message_content_en",
            "message_detected_language_code": "message_detected_language_code",
            "item_type": "MESSAGE",
            "item_created_datetime": "2024-05-20T10:00:00",
        }
    ]
}


@patch(
    "genie_dao.services.conversation.conversation_db_service.create_flow_supervisor_state",
    return_value=AsyncMock,
)
@patch(
    "genie_dao.services.conversation.conversation_db_service.create_conversation",
    return_value=AsyncMock,
)
@patch(
    "genie_dao.services.conversation.conversation_db_service.check_and_get_conversation",
    return_value=AsyncMock,
)
@patch(
    "genie_dao.services.conversation.conversation_db_service.get_conversation_messages",
    return_value=AsyncMock,
)
@patch(
    "genie_dao.services.conversation.conversation_db_service.end_conversation",
    return_value=AsyncMock,
)
@patch(
    "genie_dao.services.conversation.conversation_db_service.get_latest_random_flow_variant_metadata",
    return_value=AsyncMock,
)
@pytest.mark.asyncio
async def test_ensure_conversation_if_exists_and_not_renew_and_message_not_exists(
    mock_get_latest_random_flow_variant_metadata,
    mock_end_conversation,
    mock_get_conversation_messages,
    mock_check_and_get_conversation,
    mock_create_conversation,
    mock_create_flow_supervisor_state,
):
    mock_check_and_get_conversation.return_value = (True, ConversationItem(**mock_response["items"][0]))  # noqa: E501
    mock_get_conversation_messages.return_value = None
    updated_mock_response = deepcopy(mock_response)
    updated_mock_response["items"][0]["conversation_state"] = "ENDED"
    mock_end_conversation.return_value = ConversationItem(**updated_mock_response["items"][0])  # noqa: E501
    mock_get_latest_random_flow_variant_metadata.return_value = Flow(**mock_flow_response)  # noqa: E501
    mock_get_latest_random_flow_variant_metadata.extract_flow_variant_id.return_value = "VARIANT_0"  # noqa: E501
    mock_create_conversation.return_value = ConversationItem(**mock_new_conversation_response["items"][0])  # noqa: E501
    mock_create_flow_supervisor_state.return_value = FlowSupervisorItem(**mock_flow_supervisor_response)  # noqa: E501

    conversation = await ensure_conversation(
        user_uid=mock_response["items"][0]["user_uid"],
        flow_type=mock_response["items"][0]["flow_type"],
        conversation_pk=mock_response["items"][0]["PK"],
        timeout_time_s=900,
        renew=False,
    )

    mock_check_and_get_conversation.assert_awaited_once()
    mock_get_conversation_messages.assert_awaited_once()
    mock_end_conversation.assert_awaited_once()
    mock_get_latest_random_flow_variant_metadata.assert_awaited_once()
    mock_create_conversation.assert_awaited_once()
    mock_create_flow_supervisor_state.assert_awaited_once()

    assert isinstance(conversation, ConversationItem)
    assert conversation.conversation_state == "ACTIVE"
    assert conversation.PK != mock_response["items"][0]["PK"]
    assert conversation.PK == mock_new_conversation_response["items"][0]["PK"]


@patch(
    "genie_dao.services.conversation.conversation_db_service.create_flow_supervisor_state",
    return_value=AsyncMock,
)
@patch(
    "genie_dao.services.conversation.conversation_db_service.create_conversation",
    return_value=AsyncMock,
)
@patch(
    "genie_dao.services.conversation.conversation_db_service.check_and_get_conversation",
    return_value=AsyncMock,
)
@patch(
    "genie_dao.services.conversation.conversation_db_service.get_conversation_messages",
    return_value=AsyncMock,
)
@patch(
    "genie_dao.services.conversation.conversation_db_service.end_conversation",
    return_value=AsyncMock,
)
@patch(
    "genie_dao.services.conversation.conversation_db_service.get_latest_random_flow_variant_metadata",
    return_value=AsyncMock,
)
async def test_ensure_conversation_if_exists_and_not_renew_and_message_exists(
    mock_get_latest_random_flow_variant_metadata,
    mock_end_conversation,
    mock_get_conversation_messages,
    mock_check_and_get_conversation,
    mock_create_conversation,
    mock_create_flow_supervisor_state,
):
    mock_check_and_get_conversation.return_value = (True, ConversationItem(**mock_response["items"][0]))  # noqa: E501
    mock_get_conversation_messages.return_value = [MessageItem(**mock_messages_response["items"][0])]  # noqa: E501
    updated_mock_response = mock_response
    updated_mock_response["conversation_state"] = "ENDED"
    mock_end_conversation.return_value = ConversationItem(**updated_mock_response["items"][0])  # noqa: E501
    mock_get_latest_random_flow_variant_metadata.return_value = Flow(**mock_flow_response)  # noqa: E501
    mock_get_latest_random_flow_variant_metadata.extract_flow_variant_id.return_value = "VARIANT_0"  # noqa: E501
    mock_create_conversation.return_value = ConversationItem(**mock_new_conversation_response["items"][0])  # noqa: E501
    mock_create_flow_supervisor_state.return_value = FlowSupervisorItem(**mock_flow_supervisor_response)  # noqa: E501

    conversation = await ensure_conversation(
        user_uid=mock_response["items"][0]["user_uid"],
        flow_type=mock_response["items"][0]["flow_type"],
        conversation_pk=mock_response["items"][0]["PK"],
        timeout_time_s=900,
        renew=False,
    )

    mock_check_and_get_conversation.assert_awaited_once()
    mock_get_conversation_messages.assert_awaited_once()
    mock_end_conversation.assert_awaited_once()
    mock_get_latest_random_flow_variant_metadata.assert_awaited_once()
    mock_create_conversation.assert_awaited_once()
    mock_create_flow_supervisor_state.assert_awaited_once()

    assert isinstance(conversation, ConversationItem)
    assert conversation.conversation_state == "ACTIVE"
    assert conversation.PK != mock_response["items"][0]["PK"]
    assert conversation.PK == mock_new_conversation_response["items"][0]["PK"]


@patch(
    "genie_dao.services.conversation.conversation_db_service.create_flow_supervisor_state",
    return_value=AsyncMock,
)
@patch(
    "genie_dao.services.conversation.conversation_db_service.create_conversation",
    return_value=AsyncMock,
)
@patch(
    "genie_dao.services.conversation.conversation_db_service.check_and_get_conversation",
    return_value=AsyncMock,
)
@patch(
    "genie_dao.services.conversation.conversation_db_service.get_latest_random_flow_variant_metadata",
    return_value=AsyncMock,
)
async def test_ensure_conversation_if_renew(
    mock_get_latest_random_flow_variant_metadata,
    mock_check_and_get_conversation,
    mock_create_conversation,
    mock_create_flow_supervisor_state,
):
    mock_check_and_get_conversation.return_value = (False, None)
    mock_get_latest_random_flow_variant_metadata.return_value = Flow(**mock_flow_response)  # noqa: E501
    mock_get_latest_random_flow_variant_metadata.extract_flow_variant_id.return_value = "VARIANT_0"  # noqa: E501
    mock_create_conversation.return_value = ConversationItem(**mock_new_conversation_response["items"][0])  # noqa: E501
    mock_create_flow_supervisor_state.return_value = FlowSupervisorItem(**mock_flow_supervisor_response)  # noqa: E501

    conversation = await ensure_conversation(
        user_uid=mock_response["items"][0]["user_uid"],
        flow_type=mock_response["items"][0]["flow_type"],
        conversation_pk=mock_response["items"][0]["PK"],
        timeout_time_s=900,
        renew=False,
    )

    mock_check_and_get_conversation.assert_awaited_once()
    mock_get_latest_random_flow_variant_metadata.assert_awaited_once()
    mock_create_conversation.assert_awaited_once()
    mock_create_flow_supervisor_state.assert_awaited_once()

    assert isinstance(conversation, ConversationItem)
    assert conversation.conversation_state == "ACTIVE"
    assert conversation.PK != mock_response["items"][0]["PK"]
    assert conversation.PK == mock_new_conversation_response["items"][0]["PK"]


async def test_create_conversation():
    mock_client_db = AsyncMock()
    mock_table = AsyncMock()

    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_client_db
    mock_client_db.Table.return_value = mock_table

    with patch("genie_dao.storage.dynamodb.DynamoDBClient", return_value=mock_context_manager):  # noqa: E501
        user_uid = mock_response["items"][0]["user_uid"]
        flow_type = mock_response["items"][0]["flow_type"]
        variant_id = mock_response["items"][0]["flow_variant_id"]

        conversation = await create_conversation(user_uid, flow_type, variant_id)

        mock_client_db.Table.assert_awaited_once_with(GLOBAL_SETTINGS.environment.value.lower() + "_" + "chatbot_table")
        mock_table.put_item.assert_awaited()

        assert isinstance(conversation, ConversationItem)
        assert conversation.flow_type == mock_response["items"][0]["flow_type"]
        assert conversation.PK.startswith(ItemType.CONVERSATION.value)


async def test_check_and_get_conversation_when_flow_type_exists_with_one_active_conversation():  # noqa: E501
    with patch(
        "genie_dao.services.conversation.conversation_db_service.query_all_items_dynamodb_table",
        new_callable=AsyncMock,
    ) as query_dynamodb_table:
        query_dynamodb_table.return_value = [mock_response["items"][0]]
        conversation_exists, conversations = await check_and_get_conversation(
            user_uid=mock_response["items"][0]["user_uid"],
            flow_type=mock_response["items"][0]["flow_type"],
            conversation_pk=None,
        )
        query_dynamodb_table.assert_awaited_once()
        assert isinstance(conversations, ConversationItem)
        assert conversation_exists == True  # noqa: E712


async def test_check_and_get_conversation_when_flow_type_exists_with_more_active_conversation():  # noqa: E501
    with patch(
        "genie_dao.services.conversation.conversation_db_service.query_all_items_dynamodb_table",
        new_callable=AsyncMock,
    ) as query_dynamodb_table:
        query_dynamodb_table.return_value = [
            mock_response_multiple_conversations["items"][0],
            mock_response_multiple_conversations["items"][1],
        ]
        conversation_exists, conversations = await check_and_get_conversation(
            user_uid=mock_response["items"][0]["user_uid"],
            flow_type=mock_response["items"][0]["flow_type"],
            conversation_pk=mock_response["items"][0]["PK"],
        )
        query_dynamodb_table.assert_awaited_once()
        assert isinstance(conversations, ConversationItem)
        assert conversation_exists == True  # noqa: E712
        assert conversations == ConversationItem(**mock_response_multiple_conversations["items"][0])  # noqa


async def test_check_and_get_conversation_when_flow_type_doesnt_exists():
    with patch(
        "genie_dao.services.conversation.conversation_db_service.query_all_items_dynamodb_table",  # noqa
        new_callable=AsyncMock,
    ) as query_dynamodb_table:
        query_dynamodb_table.return_value = mock_null_response
        conversation_exists, conversations = await check_and_get_conversation(
            user_uid=mock_response["items"][0]["user_uid"],
            flow_type=mock_response["items"][0]["flow_type"],
            conversation_pk=mock_response["items"][0]["PK"],
        )
        query_dynamodb_table.assert_awaited_once()
        assert conversations is None
        assert conversation_exists is False


@patch(
    "genie_dao.services.conversation.conversation_db_service.get_conversation_by_pk",
    return_value=AsyncMock,
)
async def test_end_conversation_if_exists(mock_get_conversation_by_pk):
    mock_client_db = AsyncMock()
    mock_table = AsyncMock()
    mock_client_db.Table.return_value = mock_table
    mock_client_db.Table.put_item.return_value = mock_table
    with patch("genie_dao.storage.dynamodb.DynamoDBClient", AsyncMock):
        mock_get_conversation_by_pk.return_value = ConversationItem(**mock_response["items"][0])  # noqa: E501
        conversation = await end_conversation(mock_response["items"][0]["conversation_uid"])  # noqa: E501
        assert conversation.conversation_state == "ENDED"
        assert conversation.conversation_uid == mock_response["items"][0]["conversation_uid"]  # noqa: E501


@patch(
    "genie_dao.services.conversation.conversation_db_service.get_conversation_by_pk",
    return_value=AsyncMock,
)
async def test_end_conversation_if_not_exists(mock_get_conversation_by_pk):
    mock_client_db = AsyncMock()
    mock_table = AsyncMock()
    mock_client_db.Table.return_value = mock_table
    mock_client_db.Table.put_item.return_value = mock_table
    with patch("genie_dao.storage.dynamodb.DynamoDBClient", AsyncMock):
        mock_get_conversation_by_pk.return_value = None
        conversation = await end_conversation("")
        assert conversation is None


async def test_get_conversation_by_pk_if_exixts():
    with patch(
        "genie_dao.services.conversation.conversation_db_service.query_all_items_dynamodb_table",  # noqa
        new_callable=AsyncMock,
    ) as query_dynamodb_table:
        query_dynamodb_table.return_value = [mock_response["items"][0]]
        conversation = await get_conversation_by_pk(mock_response["items"][0]["conversation_uid"])  # noqa: E501
        query_dynamodb_table.assert_awaited_once()
        assert isinstance(conversation, ConversationItem)
        assert conversation.PK == mock_response["items"][0]["PK"]
        assert conversation.SK.startswith(ItemType.METADATA.value)


async def test_get_conversation_by_pk_if_not_exixts():
    with patch(
        "genie_dao.services.conversation.conversation_db_service.query_all_items_dynamodb_table",  # noqa
        new_callable=AsyncMock,
    ) as query_dynamodb_table:
        query_dynamodb_table.return_value = mock_null_response
        conversation = await get_conversation_by_pk("")
        query_dynamodb_table.assert_awaited_once()
        assert conversation is None


async def test_get_conversations():
    with patch(
        "genie_dao.services.conversation.conversation_db_service.query_all_items_dynamodb_table",  # noqa
        new_callable=AsyncMock,
    ) as query_all_items_dynamodb_table:
        query_all_items_dynamodb_table.return_value = [mock_response["items"][0]]
        conversations_list = await get_conversations(
            partition_date=mock_response["items"][0]["conversation_start_datetime"]  # noqa
        )
        assert isinstance(conversations_list, list)
        assert isinstance(conversations_list[0], ConversationItem)
        assert conversations_list[0].PK == mock_response["items"][0]["PK"]
        assert conversations_list[0].SK.startswith(ItemType.METADATA.value)
