import dataclasses

from genie_dao.storage.dynamodb import (
    DynamoDataType,
    DynamoDBTable,
    DynamoKeyType,
    DynamoTableAttribute,
    DynamoTableKeyAttribute,
)


@dataclasses.dataclass
class WhatsappInputMessageItem:
    """Corresponds to a data item part of `WhatsappInputMessageTable`.

    user_id: WhatsApp user id, usually a phone number
    sent_datetime: message sent timestamp
    business_uid: Business account id in this message, usually a business account phone number
    type: WhatsApp message type, currently should be text only
    content: WhatsApp message content
    wam_id: WhatsApp message id
    is_handled: if this message is handled by our service
    in_or_outbound_message: if this is a message from user, then inbound, if from business phone
        number then outbound
    """

    user_id: str
    sent_datetime: str
    business_uid: str
    type: str
    content: str
    wam_id: str
    is_handled: bool


class WhatsappInputMessageTable(DynamoDBTable):
    """DynamoDB table to persist Whatsapp incoming messages.

    The partition key is "conversation_uid". This allows us to retrieve all messages
    belonging to the same conversation, by querying only on "conversation_id".

    The sort key within each partition is the message uid, a string of 16 bytes uniquely
    identifying each message.
    """

    name = "whatsapp_message"

    key_schema = [
        DynamoTableKeyAttribute(
            name="user_id",
            type=DynamoKeyType.HASH,
        ),
        DynamoTableKeyAttribute(
            name="sent_datetime",
            type=DynamoKeyType.RANGE,
        ),
    ]

    attributes = [
        DynamoTableAttribute(name="user_id", type=DynamoDataType.string),
        DynamoTableAttribute(name="sent_datetime", type=DynamoDataType.string),
    ]
