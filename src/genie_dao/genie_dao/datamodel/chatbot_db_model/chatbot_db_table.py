import contextvars
from typing import Union

from aioboto3.dynamodb import table as dynamodb_table

from genie_dao.storage.dynamodb import (
    DynamoAttributeProjectionType,
    DynamoDataType,
    DynamoDBTable,
    DynamoKeyType,
    DynamoTableAttribute,
    DynamoTableGlobalSecondaryIndex,
    DynamoTableKeyAttribute,
)


class ChatbotTable(DynamoDBTable):
    """Main DynamoDB table to hold chat items.

    The partition key is `pk`, it could be prefixed with either:
    - FLOW -> To indicate a flow type
    - CONVERSATION -> To access conversation related information
    - USER -> To access user related information
    - ANALYTICS (TBD)

    This structure is a single table design and it allows to:
        -   Query conversations, get its messages, get the AI states associated
        -   Get/Set flow information
    """

    name = "chatbot_table"

    billing_mode = "PAY_PER_REQUEST"

    key_schema = [
        DynamoTableKeyAttribute(
            name="PK",
            type=DynamoKeyType.HASH,
        ),
        DynamoTableKeyAttribute(
            name="SK",
            type=DynamoKeyType.RANGE,
        ),
    ]

    attributes = [
        DynamoTableAttribute(name="PK", type=DynamoDataType.string),
        DynamoTableAttribute(name="SK", type=DynamoDataType.string),
        DynamoTableAttribute(name="user_uid", type=DynamoDataType.string),
        DynamoTableAttribute(name="item_type", type=DynamoDataType.string),
    ]

    global_secondary_indexes = [
        DynamoTableGlobalSecondaryIndex(
            name="UserConversationsIndex",
            key_schema=[
                DynamoTableKeyAttribute(name="user_uid", type=DynamoKeyType.HASH),
                DynamoTableKeyAttribute(name="SK", type=DynamoKeyType.RANGE),
            ],
            projection_type=DynamoAttributeProjectionType.INCLUDE,
            projection_non_key_attributes=[
                "PK",
                "flow_type",
                "flow_variant_id",
                "conversation_uid",
                "conversation_state",
                "conversation_start_datetime",
                "conversation_end_datetime",
                "item_type",
                "item_created_datetime",
            ],
        ),
        DynamoTableGlobalSecondaryIndex(
            name="ItemTypeIndex",
            key_schema=[
                DynamoTableKeyAttribute(name="item_type", type=DynamoKeyType.HASH),
            ],
            projection_type=DynamoAttributeProjectionType.INCLUDE,
            projection_non_key_attributes=[
                "PK",
                "SK",
                "user_uid",
                "flow_type",
                "flow_variant_id",
                "conversation_uid",
                "conversation_state",
                "conversation_start_datetime",
                "conversation_end_datetime",
                "item_created_datetime",
            ],
        ),
    ]

    writer_ctx: contextvars.ContextVar[
        Union[dynamodb_table.TableResource, dynamodb_table.BatchWriter, None]
    ] = contextvars.ContextVar("dynamodb_chatbot_table_writer", default=None)
