from typing import Optional

from connectai.handlers.api.errors import ConversationNotFound
from connectai.handlers.internal_bus.session_bus import ConversationSessionBus
from connectai.handlers.metrics import prometheus
from connectai.handlers.utils.calculator_utils import placeholder_calculator
from connectai.modules.datamodel import (
    AgentResponsePayload,
    AgentResponseRequestPayload,
    Conversation,
    LLMDelimeters,
    MessageType,
    OutputMessage,
    RuntimeContext,
    TranslationLanguages,
)
from connectai.modules.state_machine.loaders.flow_factory import FlowFactory
from genie_core.utils import logging
from genie_core.utils.helpers import flatten_nested_dict
from genie_dao.services.ai_state import create_external_conversation_customer_context
from genie_dao.services.conversation.conversation_db_service import (
    check_and_get_conversation,
    ensure_conversation,
)
from genie_dao.services.message.message_db_service import (
    create_message,
    get_conversation_messages,
)

_log = logging.get_or_create_logger(logger_name="AgentResponse")


async def handle_conversation_flow(
    request_payload: AgentResponseRequestPayload,
    session_bus: ConversationSessionBus,
) -> Optional[AgentResponsePayload]:
    """Handles the conversation flow.

    This function handles the conversation flow for a given user.
    Steps taken are:
    - Get the flow type from the request payload.
    - Get the conversation from the database.
    - Instantiate the flow state machine from the database.
    - Create the user message if it's not the first reach or if the first message is not from the AI.
    - Prepare conversation data for the flow.
    - Run the flow.
    - Return the response.
    """
    prometheus.conversations_handled.inc()
    prometheus.nb_active_conversations.inc()

    # 1 - Get the flow type from the request payload
    flow_type = request_payload.flow_id

    with prometheus.response_latency.labels(flow_id=flow_type).time():
        _log.info(f"Use case: {flow_type}")

        if request_payload.conversation_pk is not None:
            _, conv = await check_and_get_conversation(
                user_uid=request_payload.user_id, flow_type=flow_type, conversation_pk=request_payload.conversation_pk
            )
        else:
            # 2 - Get the conversation from the database
            conv = await ensure_conversation(
                conversation_pk=request_payload.conversation_pk,
                user_uid=request_payload.user_id,
                flow_type=flow_type,
                renew=request_payload.force_new_conversation,
            )

        if conv is None:
            raise ConversationNotFound()

        # Set the conversation ID in the session bus
        session_bus.set_conversation_id(conv.PK)

        # 3 - Instantiate the flow state machine from the database
        _log.debug(f"Flow variant is {conv.flow_variant_id} for user {request_payload.user_id}")
        flow_factory = FlowFactory(flow_type=flow_type, flow_variant_number=int(conv.flow_variant_id.split("_")[-1]))
        flow = await flow_factory.create_flow_from_db()
        messages = await get_conversation_messages(conversation_uid=conv.PK)
        is_first_message = not len(messages)
        user_message = None

        # TODO: This is a temporary fix to ensure that the translation service is disabled
        flow.flow_config.translation_service_enabled = False

        # 4 - Create the user message if it's not the first reach or if the first message is not from the AI
        if not is_first_message or (not flow.flow_config.is_ai_first_message and is_first_message):
            if not request_payload.message.content:
                """First message can be empty, when the caller has no idea if the flow
                should be started by user or AI message.

                This conditional early return makes sure we instantiate the
                conversation, but await the actual message from user, which will be
                handled on subsequent invocation of this method
                """

                session_bus.publish_chunk(message_content=LLMDelimeters.END.value)
                await session_bus.publish_response_completed()
                return AgentResponsePayload(
                    conversation_id=conv.PK,
                    response_completed=True,
                )

            _log.info(f"Creating user message: {request_payload.message}")
            user_message = await create_message(
                conversation_uid=conv.PK,
                message_type=MessageType.input,
                raw_message_content=request_payload.message.content,
                raw_message_language_code=TranslationLanguages.AUTO.value,
                translate_target_language=TranslationLanguages.ENGLISH.value,
                is_translation_enabled=flow.flow_config.translation_service_enabled,
            )
            messages.append(user_message)

        # 5 - Prepare conversation data for the flow
        conversation, customer_data = await _prepare_conversation_data(conv, messages, request_payload, flow_type)
        # Flatten the external API data
        external_data_flattened = (
            flatten_nested_dict(request_payload.conversation_context.external_data)
            if request_payload.conversation_context.external_data
            else {}
        )

        context = await create_external_conversation_customer_context(
            conversation_uid=conv.PK, customer_context=external_data_flattened
        )
        _log.info(f"Latest External data: {context}")

        # 6 - Run the flow
        response = await flow.run(
            session_bus=session_bus,
            runtime_context=RuntimeContext(
                conversation=conversation,
                extra_info={
                    "is_first_reach": is_first_message,
                    "user_input": user_message.message_content_en if user_message else request_payload.message,
                    "user_message_uid": user_message.message_uid if user_message else None,
                    "flow_type": flow_type,
                    **customer_data,
                    **external_data_flattened,
                },
                translation_service_enabled=flow.flow_config.translation_service_enabled,
            ),
        )

        prometheus.nb_active_conversations.dec()

        # 7 - Return the response
        return AgentResponsePayload(
            message=OutputMessage(content=response.llm_response),
            llm_features=response.llm_features,
            conversation_features=response.dialogue_features,
            customer_features=response.customer_features,
            conversation_ended_flag=response.conversation_ended_flag,
            conversation_id=conv.PK,
            message_id=user_message.message_uid if user_message else None,
            response_completed=True,
        )


async def _prepare_conversation_data(conv, messages, request_payload, flow_type) -> tuple[Conversation, dict]:
    """Prepare conversation data for the flow.

    :param ConversationItem conv: The database conversation object. :param
        list[MessageItem] messages: List of conversation's messages created up until
        this point
    :param AgentResponseRequestPayload request_payload: The request payload.
    :param str flow_type: The flow type/name.
    :return: The conversation object and the customer data.
    :rtype: tuple[Conversation, dict]
    """
    conversation = Conversation(conversation_uid=conv.PK)
    conversation.build_new_conversation_history(messages)
    # Transform customer information into flattened dictionary
    customer_data = request_payload.to_dict()["conversation_context"]["customer_context"]

    try:
        # TODO: abstract calculator to be part of data connectors
        customer_data = placeholder_calculator(customer_data, flow_type) if customer_data else {}
    except TypeError as e:
        _log.warn(f"TypeError in placeholder_calculator, API input missing: {e}")

    return conversation, customer_data
