from unittest.mock import AsyncMock, patch

from connectai.modules.datamodel import TranslatedData
from genie_core.utils import logging
from genie_dao.datamodel.chatbot_db_model.models import ItemType, MessageItem
from genie_dao.services.message.message_db_service import (
    _handle_message_translation,
    create_message,
    get_conversation_messages,
)

_log = logging.get_or_create_logger(logger_name="MessageDBService")

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

mocked_translated_data_response = {
    "translated_text": "response_translated_text",
    "source_language_code": "response_source_language_code",
    "target_language_code": "response_target_source_language_code",
}


async def test_create_message() -> MessageItem:
    mock_client_db = AsyncMock()
    mock_table = AsyncMock()

    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_client_db
    mock_client_db.Table.return_value = mock_table

    with patch("genie_dao.storage.dynamodb.DynamoDBClient", return_value=mock_context_manager):  # noqa: E501
        with patch(
            "genie_dao.services.message.message_db_service._handle_message_translation",
            new_callable=AsyncMock,
        ) as _handle_message_translation:
            _handle_message_translation.return_value = ("Hello dummy values", "en")
            response = await create_message(
                conversation_uid=mock_messages_response["items"][0]["PK"],
                raw_message_content="hello dummy values",
                raw_message_language_code=mocked_translated_data_response["source_language_code"],
                translate_target_language=mocked_translated_data_response["target_language_code"],
                is_translation_enabled="False",
                message_type=mock_messages_response["items"][0]["message_type"],
            )

            assert isinstance(response, MessageItem)
            assert response.PK == mock_messages_response["items"][0]["PK"]
            assert response.SK.startswith(ItemType.MESSAGE.value)


async def test_dispatch_pubsub_message(pubsub_publish):
    mock_client_db = AsyncMock()
    mock_table = AsyncMock()

    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_client_db
    mock_client_db.Table.return_value = mock_table

    with patch("genie_dao.storage.dynamodb.DynamoDBClient", return_value=mock_context_manager):  # noqa: E501
        with patch(
            "genie_dao.services.message.message_db_service._handle_message_translation",
            new_callable=AsyncMock,
        ) as _handle_message_translation:
            _handle_message_translation.return_value = ("Hello dummy values", "en")
            response = await create_message(
                conversation_uid=mock_messages_response["items"][0]["PK"],
                raw_message_content="hello dummy values",
                raw_message_language_code=mocked_translated_data_response["source_language_code"],
                translate_target_language=mocked_translated_data_response["target_language_code"],
                is_translation_enabled="False",
                message_type=mock_messages_response["items"][0]["message_type"],
            )

            pubsub_publish.assert_called_once()
            assert str(pubsub_publish.call_args_list[0].args[0]) == f"conversation:97869P21HG7OTRFW"
            assert pubsub_publish.call_args_list[0].args[1].name == "message_created"


async def test_handle_message_translation_if_translation_not_enabled() -> tuple[str, str]:  # noqa: E501
    raw_message_content = "Hello dummy values"
    raw_message_language_code = "en"
    translate_target_language = "en"
    is_translation_enabled = False

    with patch(
        "genie_dao.services.message.message_db_service.translate",
        new_callable=AsyncMock,
    ) as translate:
        translate.return_value = TranslatedData(**mocked_translated_data_response)

        await _handle_message_translation(
            raw_message_content=raw_message_content,
            raw_message_language_code=raw_message_language_code,
            translate_target_language=translate_target_language,
            is_translation_enabled=is_translation_enabled,
        )
        translate.assert_not_called()


async def test_handle_message_translation_if_src_and_tgt_message_code_matches_and_tgt_code_is_en() -> tuple[str, str]:
    raw_message_content = "Hello dummy values"
    raw_message_language_code = "en"
    translate_target_language = "en"
    is_translation_enabled = True

    with patch(
        "genie_dao.services.message.message_db_service.translate",
        new_callable=AsyncMock,
    ) as translate:
        translate.return_value = TranslatedData(**mocked_translated_data_response)

        await _handle_message_translation(
            raw_message_content=raw_message_content,
            raw_message_language_code=raw_message_language_code,
            translate_target_language=translate_target_language,
            is_translation_enabled=is_translation_enabled,
        )
        translate.assert_not_called()


async def test_handle_message_translation_if_src_and_tgt_message_code_not_matches_and_tgt_code_is_not_en():  # noqa
    raw_message_content = "Hello dummy values"
    raw_message_language_code = "hi"
    translate_target_language = "sp"
    is_translation_enabled = True

    with patch("genie_dao.services.message.message_db_service.translate", new_callable=AsyncMock) as translate:
        translate.return_value = TranslatedData(**mocked_translated_data_response)

        await _handle_message_translation(
            raw_message_content=raw_message_content,
            raw_message_language_code=raw_message_language_code,
            translate_target_language=translate_target_language,
            is_translation_enabled=is_translation_enabled,
        )
        translate.assert_awaited_once()


async def test_handle_message_translation_if_src_and_tgt_message_code_not_matches_and_tgt_code_is_en():  # noqa
    raw_message_content = "Hello dummy values"
    raw_message_language_code = "hi"
    translate_target_language = "en"
    is_translation_enabled = True

    with patch("genie_dao.services.message.message_db_service.translate", new_callable=AsyncMock) as translate:
        translate.return_value = TranslatedData(**mocked_translated_data_response)  # noqa

        await _handle_message_translation(
            raw_message_content=raw_message_content,
            raw_message_language_code=raw_message_language_code,
            translate_target_language=translate_target_language,
            is_translation_enabled=is_translation_enabled,
        )
        translate.assert_awaited_once()


async def test_get_conversation_messages() -> list[MessageItem]:
    with patch(
        "genie_dao.services.message.message_db_service.query_dynamodb_table",
        new_callable=AsyncMock,
    ) as query_dynamodb_table:
        query_dynamodb_table.return_value = mock_messages_response
        await get_conversation_messages("mock_conversation_uid")
        query_dynamodb_table.assert_awaited_once()
