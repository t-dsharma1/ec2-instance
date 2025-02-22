from datetime import datetime

from genie_core.utils import logging
from genie_dao import pubsub
from genie_dao.datamodel._translation import TranslationLanguages
from genie_dao.datamodel.chatbot_db_model import ChatbotTable
from genie_dao.datamodel.chatbot_db_model.models import ItemType, MessageItem
from genie_dao.pubsub.chatbot.models import ChatbotMessageCreated, ConversationChannel
from genie_dao.services.translation.translation_service import translate
from genie_dao.storage.dynamodb import DynamoDBWriter
from genie_dao.storage.operations import query_dynamodb_table

_log = logging.get_or_create_logger(logger_name="MessageDBService")


@ChatbotTable.inject_writer
async def create_message(
    conversation_uid: str,
    raw_message_content: str,
    message_type: str,
    raw_message_language_code: str,
    translate_target_language: str,
    is_translation_enabled: bool,
    writer: DynamoDBWriter,
) -> MessageItem:
    """Create a new message within a conversation.

    Parameters:
    - conversation_uid (str): The conversation UID.
    - raw_message_content (str): The raw message content.
    - message_type (str): The message type.
    - raw_message_language_code (str): The language code of the raw message.
    - translate_target_language (str): The target language to translate the message to.

    Returns:
    - MessageItem: The created message item.
    """

    message_sent_datetime: str = datetime.now().isoformat()
    message_uid = ItemType.MESSAGE.value + "#" + "".join(message_sent_datetime)

    message_content_en, message_detected_language_code = await _handle_message_translation(
        raw_message_content=raw_message_content,
        raw_message_language_code=raw_message_language_code,
        translate_target_language=translate_target_language,
        is_translation_enabled=is_translation_enabled,
    )

    item = {
        "PK": conversation_uid,
        "SK": message_uid,
        "message_uid": message_uid,
        "message_sent_datetime": message_sent_datetime,
        "message_type": message_type,
        "message_content": raw_message_content,  # Original message content
        "message_content_en": message_content_en,  # Translated message content
        "message_detected_language_code": message_detected_language_code,
        "item_type": ItemType.MESSAGE.value,
        "item_created_datetime": message_sent_datetime,
    }

    async def on_commit():
        pubsub.publish(
            ConversationChannel(conversation_pk=conversation_uid), ChatbotMessageCreated(data=MessageItem(**item))
        )

    writer.register_on_commit_hook(on_commit)
    await writer.put_item(Item=item)
    return MessageItem(**item)


async def _handle_message_translation(
    raw_message_content: str,
    raw_message_language_code: str,
    translate_target_language: str,
    is_translation_enabled: bool,
) -> tuple[str, str]:
    """Translate a message to a target language. The possibilities are:

    - Translate the message to English.
    - Translate the message to a target language.
    - No translation needed (If raw and target languages are the same).


    Parameters:
    - raw_message_content (str): The raw message content.
    - raw_message_language_code (str): The language code of the raw message.
    - translate_target_language (str): The target language to translate the message to.

    Returns:
    - tuple: The translated message content and the detected language code.
    """

    if not is_translation_enabled:
        """No need to translate the message.

        Return the raw message content and language code.
        """
        return raw_message_content, raw_message_language_code

    message_content_en = None
    message_detected_language_code = (
        TranslationLanguages.AUTO.value
    )  # Default to english (LLM always sends english messages)

    if raw_message_language_code == translate_target_language:
        # No need to translate (because both raw_message_language_code and translate_target_language are english)
        message_content_en = raw_message_content
        message_detected_language_code = raw_message_language_code
    else:
        # Translate the message to English
        if translate_target_language == TranslationLanguages.ENGLISH.value:
            translated_data = await translate(
                text=raw_message_content,
                source_language_code=TranslationLanguages.AUTO.value,
                target_language_code=TranslationLanguages.ENGLISH.value,
            )
            message_content_en = translated_data.translated_text
            message_detected_language_code = translated_data.source_language_code
        else:
            translated_data = await translate(
                text=raw_message_content,
                source_language_code=TranslationLanguages.ENGLISH.value,
                target_language_code=translate_target_language,
            )
            message_content_en = translated_data.translated_text
            message_detected_language_code = translated_data.source_language_code

    return message_content_en, message_detected_language_code


async def get_conversation_messages(conversation_uid: str) -> list[MessageItem]:
    """Retrieve all messages for a given conversation.

    Parameters:
    - conversation_uid (str): The conversation UID to retrieve messages for.

    Returns:
    - list: A list of message items for the conversation.
    """
    key_condition_expression = "PK = :pk AND begins_with(SK, :sk_prefix)"

    expression_attribute_values = {":pk": conversation_uid, ":sk_prefix": ItemType.MESSAGE.value + "#"}

    # Assuming the query function returns items sorted by sort key in ascending order
    messages = (
        await query_dynamodb_table(
            table_name=ChatbotTable.get_table_name(),
            key_condition_expression=key_condition_expression,
            expression_attribute_values=expression_attribute_values,
            consistent_read=True,
        )
    )["items"]

    return [MessageItem(**m) for m in messages]
