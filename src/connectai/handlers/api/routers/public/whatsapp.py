import os
from typing import Annotated

import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Body, HTTPException, Request, Response

from connectai.handlers.api import models
from connectai.handlers.queue.sqs import (
    SQSMessageHandler,
    SQSQueueListener,
    SQSQueuePublisher,
)
from connectai.handlers.queue.worker import process_queue_message
from connectai.modules.datamodel import WorkQueueItem
from connectai.settings import GLOBAL_SETTINGS
from genie_core.utils import logging

_log = logging.get_or_create_logger(logger_name="apiPublicWAHook")

router = APIRouter()

queue_publisher = SQSQueuePublisher(
    reference_queue_name=GLOBAL_SETTINGS.environment.value.lower()
    + "_"
    + GLOBAL_SETTINGS.platform_base_domain
    + "_"
    + GLOBAL_SETTINGS.chatbot_queue_name
)

queue_message_runner = SQSMessageHandler(process_message_callback=process_queue_message)
queue_listener = SQSQueueListener(
    message_handler=queue_message_runner,
    reference_queue_name=GLOBAL_SETTINGS.environment.value.lower()
    + "_"
    + GLOBAL_SETTINGS.platform_base_domain
    + "_"
    + GLOBAL_SETTINGS.chatbot_queue_name,
)
queue_listener.start_listening()


def check_phone_number_exists(phone_number):
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
            return True
        else:
            return False


@router.post(
    "/whatsapp-hook",
    summary="WhatsApp webhook to receive incoming messages from vanilla WhatsApp events.",
)
def whatsapp_hook(request: Annotated[models.WhatsAppHookRequest, Body(embed=False)]):
    _log.info(str(request))
    _log.info(request.entry[0].changes[0].value.messages[0].text)
    _log.info(request.entry[0].changes[0].value.messages[0].timestamp)
    _log.info(request.entry[0].changes[0].value.contacts[0].profile.name)

    wa_business_nr = request.entry[0].changes[0].value.metadata.display_phone_number

    if check_phone_number_exists(wa_business_nr):
        queue_publisher.push(
            WorkQueueItem(
                chat_message=request.entry[0].changes[0].value.messages[0].text.body,
                chat_timestamp=request.entry[0].changes[0].value.messages[0].timestamp,
                from_number=request.entry[0].changes[0].value.messages[0].from_,
                to_number=request.entry[0].changes[0].value.metadata.display_phone_number,
                business_id=request.entry[0].id,
                session_id=request.entry[0].changes[0].value.messages[0].id,
                source="default",
            )
        )

        return "OK"
    else:
        _log.info(f"{wa_business_nr} is not allowed for this platform, ignoring from the queue")
        return "OK"


@router.get("/whatsapp-hook")
async def verify_webhook(request: Request):
    # Retrieve the query parameters
    query_params = request.query_params

    # Get the environment variable storing the verify token
    verify_token = "Genie"

    # Extract parameters from the webhook verification request
    mode = query_params.get("hub.mode")
    token = query_params.get("hub.verify_token")
    challenge = query_params.get("hub.challenge")

    # Check if both mode and token are present
    if mode and token:
        # Validate the mode and the token
        if mode == "subscribe" and token == verify_token:
            _log.info("WEBHOOK_VERIFIED")
            return Response(content=challenge, media_type="text/plain", status_code=200)
        else:
            # Respond with 403 Forbidden if verify tokens do not match
            raise HTTPException(status_code=403, detail="Forbidden: Invalid token or mode")
    else:
        # If required parameters are missing, respond with 400 Bad Request
        raise HTTPException(status_code=400, detail="Bad Request: Missing parameters")
