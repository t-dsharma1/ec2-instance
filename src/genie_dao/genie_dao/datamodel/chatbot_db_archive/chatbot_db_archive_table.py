from genie_dao.storage.dynamodb import (
    DynamoDataType,
    DynamoDBTable,
    DynamoKeyType,
    DynamoTableAttribute,
    DynamoTableKeyAttribute,
)


class ChatbotArchiveTable(DynamoDBTable):
    """DynamoDB table to store the archive/old conversations.

    The partition key is `pk`. The sort key is `sk`.
    """

    name = "chatbot_archive_table"

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
    ]
