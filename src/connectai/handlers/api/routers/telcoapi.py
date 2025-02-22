import asyncio
import json

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi_keycloak import OIDCUser
from starlette.websockets import WebSocketState
from uvicorn.protocols.utils import ClientDisconnected

from connectai.handlers.api.conversation_flow import handle_conversation_flow
from connectai.handlers.api.errors import ConversationNotFound
from connectai.handlers.internal_bus.session_bus import ConversationSessionBus
from connectai.handlers.internal_bus.shared_pubsub import PublicPubSub, PubSubKey
from connectai.handlers.utils.api_idp import UserRoles, idp
from connectai.modules.datamodel import (
    AgentResponsePayload,
    AgentResponseRequestPayload,
    Campaign,
    ConversationContext,
    CustomerInformation,
    EndConversationRequestPayload,
    InputMessage,
)
from connectai.modules.datamodel._api import StartConversationRequestPayload
from connectai.modules.datamodel._plans import ProductContext
from genie_core.utils import logging
from genie_dao.datamodel._customers import Customer
from genie_dao.datamodel.chatbot_db_model import ChatbotTable, ConversationItem
from genie_dao.services import end_conversation as end_conversation_db_service
from genie_dao.services import ensure_conversation

_log = logging.get_or_create_logger(logger_name="TelcoAPI")

router = APIRouter()


@router.get("/health")
def health_check(current_user: OIDCUser = Depends(idp.get_current_user())):
    """Health check."""
    _log.info(f"user is {current_user}")
    return {"status": "ok"}


@router.api_route(
    "/get-agent-response",
    methods=["POST"],
    dependencies=[Depends(idp.get_current_user(required_roles=[UserRoles.AGENT_RESPONSE]))],
)
@ChatbotTable.batch_write_transaction()
async def agent_response(request_payload: AgentResponseRequestPayload) -> AgentResponsePayload:
    """Handle agent response.

    This endpoint is the main platform entry point. It is used to handle agent response.
    It takes the standardized user request as input and returns the agent response.
    """
    customer_context = request_payload.to_dict()["conversation_context"]["customer_context"]
    request_payload.conversation_context.customer_context = CustomerInformation.load(customer_context)
    session_bus = ConversationSessionBus(shared_pubsub=PublicPubSub())
    return await handle_conversation_flow(request_payload, session_bus)


@router.post(
    "/end_conversation",
    dependencies=[Depends(idp.get_current_user(required_roles=[UserRoles.AGENT_END_CONVERSATION]))],
)
async def end_conversation(request_payload: EndConversationRequestPayload):
    """End conversation.

    This endpoint is used to end a conversation.
    """
    await end_conversation_db_service(conversation_uid=request_payload.conversation_id)


@router.post(
    "/start-conversation", dependencies=[Depends(idp.get_current_user(required_roles=[UserRoles.AGENT_RESPONSE]))]
)
async def start_conversation(request_payload: StartConversationRequestPayload) -> ConversationItem:
    """Used to start a conversation before actually sending any messages.

    It enables admin panel UI to create a conversation, and redirect to a details page
    (basically simplifies deep-linking).
    """
    return await ensure_conversation(
        user_uid=request_payload.user_id,
        flow_type=request_payload.flow_id,
        renew=True,
    )


@router.websocket("/agent-response")
async def agent_response_stream(websocket: WebSocket):
    # TODO: Add authentication
    await websocket.accept()

    session_bus = ConversationSessionBus(shared_pubsub=PublicPubSub())

    def on_receive_response(key: PubSubKey, message: AgentResponsePayload) -> None:
        """Sends the AI response back through the websocket.

        Response can be:
        - A single chunk (e.g. a word or part of a word)
        - A full text (e.g. a sentence or a paragraph) --> At the moment it is not possible to send a full text

        Args:
            key (PubSubKey): The callback pubsub key.
            message (AgentResponsePayload): The AI response chunk.
        """

        async def _execute():
            try:
                _log.info(f"Sending AI response: {message.to_json()}")
                await websocket.send_text(str(message.to_json()))
            except ClientDisconnected:
                pass

        loop = asyncio.get_event_loop()
        loop.create_task(_execute())

    async def handle_user_message(message_data: dict):
        message = message_data.pop("message", {"content": None})
        conversation_context = message_data.pop("conversation_context", {})

        def extract_context(cls, attr_name):
            value = conversation_context.pop(attr_name, None)
            if not value:
                return None
            return cls(**value)

        await handle_conversation_flow(
            session_bus=session_bus,
            request_payload=AgentResponseRequestPayload(
                **message_data,
                message=InputMessage(content=message.get("content", "")),
                conversation_context=ConversationContext(
                    customer_context=extract_context(Customer, "customer_context"),
                    product_context=extract_context(ProductContext, "product_context"),
                    campaign_context=extract_context(Campaign, "campaign_context"),
                    external_data=conversation_context.pop("external_data", {}),
                ),
            ),
        )

    session_bus.subscribe_to_llm_chunk_response(
        subscriber_id="llm_response_streamer",
        callback=on_receive_response,
    )
    session_bus.subscribe_to_response_completed(
        subscriber_id="llm_response_streamer",
        callback=on_receive_response,
    )
    try:
        msg_data = await websocket.receive_json()

        async with ChatbotTable.batch_write_transaction() as chatbot_table_batch:
            try:
                await handle_user_message(msg_data)
            except ConversationNotFound:
                await websocket.send_text(
                    json.dumps(
                        {
                            "error": "ConversationNotFound",
                        }
                    )
                )
                chatbot_table_batch.rollback()

            ack_data = await websocket.receive_json()

            if "rollback" in ack_data:
                chatbot_table_batch.rollback()
                return

            if "commit" in ack_data:
                await chatbot_table_batch.commit()
                return

    except WebSocketDisconnect:
        pass
    except Exception:
        raise
    finally:
        await session_bus.clear_all_listeners()
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
