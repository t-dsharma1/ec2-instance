import json
from typing import Callable

import httpx
from httpx import BasicAuth

from connectai.handlers.callsight.types import CallsightResponseFactory
from connectai.modules.datamodel import Conversation
from connectai.settings import GLOBAL_SETTINGS
from genie_core.utils import logging
from genie_dao.services.callsight.callsight_db_service import (
    get_latest_callsight_pipeline,
)
from genie_dao.services.message.message_db_service import get_conversation_messages

_log = logging.get_or_create_logger(logger_name="Callsight")


async def get_pipeline_definition(flow_id: str):
    """Get the pipeline definition for the Callsight API.

    Params
        flow_id: str - The flow id
    """
    callsight_pipeline = await get_latest_callsight_pipeline(flow_id)
    return json.dumps(callsight_pipeline)


async def get_input_data(conversation_pk: str):
    """Get the input data for the Callsight API.

    Params
        conversation_pk: str - The conversation primary key
    """
    raw_messages = await get_conversation_messages(conversation_uid=conversation_pk)
    conversation = Conversation(conversation_uid=conversation_pk)
    conversation_transcript = conversation.build_callsight_conversation_transcript(raw_messages)
    return {"transcript": conversation_transcript}


async def run_callsight_pipeline(flow_id: str, conversation_pk: str, async_callback: Callable = None) -> str | None:
    """Prepare and send the request to Callsight API to run the pipeline.

    Params
        flow_id: str - The flow id
        conversation_pk: str - The conversation primary key
        async_callback: Callable - The callback function

    Returns
        raw_callsight_response: str - The raw string formatted json response from the Callsight API
    """

    CALLSIGHT_URL = GLOBAL_SETTINGS.callsight_url
    CALLSIGHT_EXECUTE_PIPELINE_ENDPOINT = GLOBAL_SETTINGS.callsight_execute_pipeline_endpoint
    CALLSIGHT_API_USERNAME = GLOBAL_SETTINGS.callsight_api_username
    CALLSIGHT_API_PASSWORD = GLOBAL_SETTINGS.callsight_api_password

    # Prepare the data to be sent to the API
    pipeline_definition = await get_pipeline_definition(flow_id)
    input_data = await get_input_data(conversation_pk)

    request_data = {
        "definition": pipeline_definition,
        "input": json.dumps(input_data),
    }

    files = []
    headers = {}

    async with httpx.AsyncClient() as client:
        try:
            # Send the request to the API
            response = await client.post(
                url=CALLSIGHT_URL + CALLSIGHT_EXECUTE_PIPELINE_ENDPOINT,
                headers=headers,
                data=request_data,
                files=files,
                auth=BasicAuth(CALLSIGHT_API_USERNAME, CALLSIGHT_API_PASSWORD),
            )
            if _valid_callsight_output(response.text):
                CallsightResponseFactory.create(json.loads(response.text))
                if async_callback:
                    await async_callback(response.text)
                return response.text
            else:
                _log.error("Invalid Callsight Response")
                return None
        except httpx.ConnectTimeout:
            _log.error("Callsight Response Timeout")


def _valid_callsight_output(raw_str_response: str) -> bool:
    """Validate the raw callsight response.

    Params
        raw_str_response: str - The raw callsight response

    Returns
        bool: The validation result
    """
    try:
        CallsightResponseFactory.create(json.loads(raw_str_response))
        return True
    except json.JSONDecodeError:
        _log.error("Failed to decode Callsight response.")
        return False
