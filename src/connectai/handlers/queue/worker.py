import asyncio
import json
import os

import boto3
from aiohttp import ClientError

from connectai.handlers.api.routers.telcoapi import agent_response
from connectai.handlers.whatsapp.send import message_whatsapp
from connectai.modules.datamodel import (
    AgentResponsePayload,
    AgentResponseRequestPayload,
    ConversationContext,
    InputMessage,
    WorkQueueItem,
)
from connectai.settings import GLOBAL_SETTINGS
from genie_core.utils import logging

_log = logging.get_or_create_logger(logger_name="QueueWorker")


def process_queue_message(message: dict) -> None:
    """Process the message from the queue.

    Args:
        message (dict): The raw message from the queue
    """
    try:
        queue_message = WorkQueueItem(**json.loads(message["Body"]))
        _log.debug(f"Received message: {queue_message}")
        # Get the response from the process_message function
        response = asyncio.run(process_message(queue_message))
        _log.debug(f"Response: {response}")
    except Exception as e:
        _log.error(f"Error processing message: {e}")


def get_phone_number_flow_info(phone_number):
    """Get the flow type for the phone number from the DynamoDB table."""

    pk_phone_number = f"waba_nr_{phone_number}"
    table_name = os.getenv("WABA_NR_TABLE_NAME", "prod_wa_nr")  # only prod table used for WABA
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    try:
        response = table.get_item(Key={"PK": pk_phone_number})
    except ClientError as e:
        _log.error("ClientError:", e.response["Error"]["Message"])
        return False
    except Exception as e:
        _log.error("Exception:", str(e))
        return False
    else:
        if "Item" in response:
            _log.info(f"found {pk_phone_number} in table {pk_phone_number}")
            # Get the flow type
            flow_type = response["Item"]["flow_type"]
            waba_url = response["Item"]["url"]
            waba_token = response["Item"]["token"]
            _log.info(f"Flow type: {flow_type}")
            return flow_type, waba_url, waba_token
        else:
            _log.info(f"Did not find {pk_phone_number} in table {pk_phone_number}")
            return None


async def process_message(queue_message: WorkQueueItem) -> str:
    """Main function to process the message from the queue.

    Args:
        queue_message (WorkQueueItem): The message from the queue

    Returns:
        str: The response from the AI
    """

    # Initialize a DynamoDB client with Boto3
    dynamodb = boto3.resource("dynamodb")
    user_info_table = dynamodb.Table(GLOBAL_SETTINGS.environment.value.lower() + "_user_info")

    user_id = queue_message.from_number
    business_id = queue_message.to_number
    flow_type, waba_url, waba_token = get_phone_number_flow_info(business_id)
    user_message = queue_message.chat_message
    user_message_timestamp = int(queue_message.chat_timestamp)
    session_id = queue_message.session_id
    if flow_type is None:
        _log.error(f"Flow type not found for phone number: {business_id}")
        return "Flow type not found"

    _log.info(f"Processing message for user: {user_id}")
    _log.info("Checking is first message")
    is_first_message: bool = handle_user_message(user_id, user_message, user_info_table, user_message_timestamp)
    _log.info(f"First message is {is_first_message}")

    _log.info("Generating payload")
    connect_ai_payload: dict = generate_payload(user_message, user_id, is_first_message)

    _log.info("Generating AI Response")
    ai_response: AgentResponsePayload = await agent_response(
        AgentResponseRequestPayload(
            flow_id=flow_type,
            user_id=user_id,
            force_new_conversation=is_first_message,
            has_opt_in=True,
            conversation_context=ConversationContext(**connect_ai_payload["conversation_context"]),
            message=InputMessage(**connect_ai_payload["message"]),
            sent_datetime=str(queue_message.chat_timestamp),
        )
    )

    ai_response_content = ai_response.message.content

    if queue_message.source == "default":
        message_whatsapp(user_id, ai_response_content, waba_url, waba_token)

    return ai_response_content


def handle_user_message(user_id, message, user_info_table, user_message_timestamp) -> bool:
    # Try to retrieve the user from the database
    response = user_info_table.get_item(Key={"user_id": user_id})
    user = response.get("Item")

    if user:
        if message.lower() == "--reset--":
            # Delete existing user record
            user_info_table.delete_item(Key={"user_id": user_id})
            # Create new user entry as it's a reset
            create_new_user(user_id, user_info_table, user_message_timestamp)
            return True  # This is the first message after reset

        elif user.get("is_first_message"):
            # Set is_first_message to false and update the record
            user_info_table.update_item(
                Key={"user_id": user_id},
                UpdateExpression="set is_first_message = :val",
                ExpressionAttributeValues={":val": False},
            )
            return False  # This was the first message

        else:
            return False  # Not the first message

    else:
        # New user
        create_new_user(user_id, user_info_table, user_message_timestamp)
        return True  # This is the first message for a new user


def create_new_user(user_id, user_info_table, user_message_timestamp):
    item = {
        "user_id": user_id,
        "first_login_time": user_message_timestamp,
        "is_first_message": True,
        "messages_in_process": 1,
        "latest_message_timestamp": user_message_timestamp,
    }
    user_info_table.put_item(Item=item)


def generate_payload(user_message, user_id, force_new_conversation) -> dict:
    return {
        "flow_id": "lead_acquisition",
        "user_id": user_id,
        "force_new_conversation": force_new_conversation,
        "has_opt_in": True,
        "conversation_context": {
            "customer_context": {
                "name": "dv_subscriber_data_4_connect_ai",
                "elements": [
                    {
                        "parameter_group": "others",
                        "parameter_data": [
                            {"parameter_name": "targeted_30day_pack", "parameter_value": None},
                            {"parameter_name": "no_of_month", "parameter_value": "242"},
                            {"parameter_name": "star_status", "parameter_value": "PLATINUM"},
                            {"parameter_name": "customer_segment", "parameter_value": "c) 650+"},
                        ],
                    },
                    {
                        "parameter_group": "pack_purchase_revenue",
                        "parameter_data": [
                            {"parameter_name": "pack_purchase_revenue_m1", "parameter_value": "586.866"},
                            {"parameter_name": "pack_purchase_revenue_m3", "parameter_value": "0"},
                            {"parameter_name": "pack_purchase_revenue_m2", "parameter_value": "890.003"},
                        ],
                    },
                    {
                        "parameter_group": "average_data_volume",
                        "parameter_data": [
                            {"parameter_name": "avg_gb_m2", "parameter_value": "468550.858"},
                            {"parameter_name": "avg_gb_m3", "parameter_value": "476043.253"},
                            {"parameter_name": "avg_gb_m1", "parameter_value": "712503.359"},
                        ],
                    },
                    {
                        "parameter_group": "average_recharge",
                        "parameter_data": [
                            {"parameter_name": "avg_recharge_m1", "parameter_value": "150.692"},
                            {"parameter_name": "avg_recharge_m2", "parameter_value": "277"},
                            {"parameter_name": "avg_recharge_m3", "parameter_value": "154.2"},
                        ],
                    },
                    {
                        "parameter_group": "pack_purchase_hit",
                        "parameter_data": [
                            {"parameter_name": "pack_purchase_hit_m3", "parameter_value": "0"},
                            {"parameter_name": "pack_purchase_hit_m2", "parameter_value": "5"},
                            {"parameter_name": "pack_purchase_hit_m1", "parameter_value": "5"},
                        ],
                    },
                ],
            },
            "product_context": {"product_subset": ["string"]},
            "campaign_context": {"audience_description": None},
        },
        "message": {
            "content": user_message,
            "sent_at": "2024-03-15T15:00:59.078161",
            "type": "INPUT",
            "language": "en",
        },
        "sent_datetime": "2024-03-15T15:00:59.078161",
    }
