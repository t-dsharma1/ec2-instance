import json
from typing import Any, Literal, Optional

from genie_core.utils import logging
from genie_dao.storage import dynamodb

_log = logging.get_or_create_logger()


async def query_dynamodb_table(
    table_name: str,
    key_condition_expression: str,
    expression_attribute_values: dict,
    filter_expression: Optional[str] = None,
    index_name: Optional[str] = None,
    consistent_read: bool = False,
    limit: Optional[int] = None,
    start_key: Optional[dict] = None,
) -> dict:
    """Query a DynamoDB table or a Global Secondary Index with pagination support.

    Parameters:
    - table_name (str): Name of the DynamoDB table to query.
    - index_name (str, optional): Name of the Global Secondary Index to query on. Pass None to query the table directly.
    - key_condition_expression (str): Condition for the query key (e.g., 'user_uid = :user_uid').
    - expression_attribute_values (dict): Values for the placeholders in the key_condition_expression.
    - filter_expression (str, optional): Additional filter for the query results.
    - limit (int, optional): The maximum number of items to evaluate (not necessarily the number of matching items).
    - start_key (dict, optional): The pagination token to start the query from a specific item.

    Returns:
    - dict: A dictionary with the query results and pagination details.
    """
    async with dynamodb.DynamoDBClient() as client_db:
        table = await client_db.Table(table_name)

        query_params = {
            "KeyConditionExpression": key_condition_expression,
            "ExpressionAttributeValues": expression_attribute_values,
        }

        if index_name:
            query_params["IndexName"] = index_name
        if consistent_read:
            query_params["ConsistentRead"] = True
        if filter_expression:
            query_params["FilterExpression"] = filter_expression
        if limit:
            query_params["Limit"] = limit
        if start_key:
            query_params["ExclusiveStartKey"] = start_key

        table_arn = await table.table_arn

        _log.debug(f"Query table {table_arn}: {json.dumps(query_params)}")
        response = await table.query(**query_params)
        result = {
            "items": response.get("Items", []),
            "count": response.get("Count", 0),
            "last_evaluated_key": response.get("LastEvaluatedKey"),
        }
        return result


async def query_all_items_dynamodb_table(
    table_name: str,
    key_condition_expression: str,
    expression_attribute_values: dict,
    filter_expression: Optional[str] = None,
    index_name: Optional[str] = None,
    consistent_read: bool = False,
):
    """Query a DynamoDB table or a Global Secondary Index returning all items. It uses
    query_dynamodb_table underneath but handles paging automatically.

    Parameters:
    - table_name (str): Name of the DynamoDB table to query.
    - index_name (str, optional): Name of the Global Secondary Index to query on. Pass None to query the table directly.
    - key_condition_expression (str): Condition for the query key (e.g., 'user_uid = :user_uid').
    - expression_attribute_values (dict): Values for the placeholders in the key_condition_expression.
    - filter_expression (str, optional): Additional filter for the query results.

    Returns:
    - dict: A dictionary with the query results and pagination details.
    """
    all_items = []
    last_evaluated_key = None
    while True:
        data = await query_dynamodb_table(
            table_name=table_name,
            key_condition_expression=key_condition_expression,
            expression_attribute_values=expression_attribute_values,
            filter_expression=filter_expression,
            index_name=index_name,
            start_key=last_evaluated_key,
            consistent_read=consistent_read,
        )
        # Append the items from the current page to the all_items list
        all_items.extend(data.get("items", []))
        # Check if there are more pages; if not, break the loop
        last_evaluated_key = data.get("last_evaluated_key")
        if not last_evaluated_key:
            break

    return all_items


# def query_dynamodb_table(
#     table_name: str,
#     key_condition_expression: str,
#     expression_attribute_values: dict,
#     filter_expression: Optional[str] = None,
#     index_name: str = None,
#     consistent_read: bool = False,
# ) -> list:
#     """Query a DynamoDB table or a Global Secondary Index.

#     Parameters:
#     - table_name (str): Name of the DynamoDB table to query.
#     - index_name (str): Name of the Global Secondary Index to query on. Pass None to query the table directly.
#     - key_condition_expression (str): Condition for the query key (e.g., 'user_uid = :user_uid').
#     - expression_attribute_values (dict): Values for the placeholders in the key_condition_expression.
#     - filter_expression (str, optional): Additional filter for the query results.

#     Returns:
#     - list: A list of items that match the query conditions.
#     """
#     # Get the DynamoDB client
#     client_db = dynamodb.DynamoDBClientSingleton.get_client()

#     # Specify the table
#     table = client_db.Table(table_name)

#     # Prepare query parameters
#     query_params = {
#         "KeyConditionExpression": key_condition_expression,
#         "ExpressionAttributeValues": expression_attribute_values,
#     }

#     if index_name:
#         query_params["IndexName"] = index_name

#     if consistent_read:
#         query_params["ConsistentRead"] = True

#     if filter_expression:
#         query_params["FilterExpression"] = filter_expression

#     # Query the table or index
#     response = table.query(**query_params)

#     # The response contains an 'Items' key with the query results
#     return response["Items"]


async def scan_dynamodb_table(
    table_name: str,
    select: Literal["ALL_ATTRIBUTES", "COUNT", "SPECIFIC_ATTRIBUTES"] = "ALL_ATTRIBUTES",
    projection_expression: Optional[str] = None,
    filter_expression: Optional[str] = None,
    expression_attribute_values: Optional[dict] = None,
    consistent_read: bool = False,
) -> list[Any]:
    """Scan a DynamoDB table.

    Parameters:
    - table_name (str): Name of the DynamoDB table to scan.
    - select (str): One of ALL_ATTRIBUTES, COUNT or SPECIFIC_ATTRIBUTES.
    - projection_expression (str): A string that identifies one or more attributes to retrieve
        from the specified table or index. Use in conjunction with select=SPECIFIC_ATTRIBUTES.
    - filter_expression(str): A string that contains conditions that DynamoDB applies after the
        Scan operation, but before the data is returned to you.
    - expression_attribute_values(dict):  Values for the placeholders in the filter_expression.

    Refer to
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/scan.html

    Returns:
    - list: A list of items as scanned.
    """
    # Get the DynamoDB client
    async with dynamodb.DynamoDBClient() as client_db:
        # Specify the table
        table = await client_db.Table(table_name)

        extra_args = {}

        if projection_expression is not None:
            extra_args["ProjectionExpression"] = projection_expression

        if filter_expression is not None:
            extra_args["FilterExpression"] = filter_expression

        if expression_attribute_values is not None:
            extra_args["ExpressionAttributeValues"] = expression_attribute_values

        if consistent_read:
            extra_args["ConsistentRead"] = True
        items = []
        try:
            done = False
            start_key = None
            while not done:
                if start_key:
                    extra_args["ExclusiveStartKey"] = start_key
                response = await table.scan(Select=select, **extra_args)
                items.extend(response.get("Items", []))
                start_key = response.get("LastEvaluatedKey", None)
                done = start_key is None
        except Exception as err:
            raise

        return items


async def delete_item(
    table_name: str,
    key: dict,
) -> None:
    """Delete an item from a DynamoDB table.

    Parameters:
    - table_name (str): Name of the DynamoDB table to scan.
    - key (dict): Key of the item to delete.

    Refer to
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb
        /client/delete_item.html

    Returns:
    - None
    """
    async with dynamodb.DynamoDBClient() as client_db:
        # Specify the table
        table = await client_db.Table(table_name)

        await table.delete_item(Key=key)
