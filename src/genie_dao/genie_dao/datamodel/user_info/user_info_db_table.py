from genie_dao.storage.dynamodb import (
    DynamoDataType,
    DynamoDBTable,
    DynamoKeyType,
    DynamoTableAttribute,
    DynamoTableKeyAttribute,
)


class UserInfoTable(DynamoDBTable):
    """DynamoDB table to check whether the user had used the chatbot before.

    The partition key is `user_id`. It contains the following attributes:
        - user_id: The user UID.
        - first_login_time: The time of the first login.
        - is_first_message: Whether the user has sent the first message.
    """

    name = "user_info"

    billing_mode = "PAY_PER_REQUEST"

    key_schema = [
        DynamoTableKeyAttribute(
            name="user_id",
            type=DynamoKeyType.HASH,
        ),
    ]

    attributes = [
        DynamoTableAttribute(name="user_id", type=DynamoDataType.string),
        # DynamoTableAttribute(name="first_login_time", type=DynamoDataType.string),
        # DynamoTableAttribute(name="is_first_message", type=DynamoDataType.string),
    ]
