from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi_keycloak import OIDCUser

from connectai.handlers import get_or_create_logger
from connectai.handlers.utils.api_idp import UserRoles, idp
from connectai.modules.datamodel import PagedResponseSchema
from connectai.modules.services.chat_view_services.chat_view_service import (
    filter_conversations,
    sort_conversations,
)
from genie_core.utils.helpers import paginate
from genie_dao.datamodel.chatbot_db_model.models import (
    CallsightItem,
    ConversationAIStateItem,
    ConversationCount,
    ConversationItem,
    ConversationTableFilterItem,
    ItemType,
    MessageItem,
)
from genie_dao.services import (
    get_ai_conversation_states,
    get_conversation_ai_state_by_message_id,
    get_conversation_by_pk,
    get_conversation_daily_count,
    get_conversation_messages,
    get_conversations,
)
from genie_dao.services.ai_state import (
    get_sorted_external_conversation_customer_context,
)
from genie_dao.services.callsight.callsight_db_service import (
    get_callsight_responses_for_conversation,
)

logger = get_or_create_logger(logger_name="chatViewAPI")

router = APIRouter()


@router.get("/conversations")
async def get_all_conversations(
    partition_date: str,
    _current_user: OIDCUser = Depends(idp.get_current_user(required_roles=[UserRoles.ADMIN_CHAT_HISTORY_VIEWER])),
    SK: Optional[str] = None,
    conversation_start_datetime: Optional[str] = None,
    user_uid: Optional[str] = None,
    flow_type: Optional[str] = None,
    flow_variant_id: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_direction: Optional[str] = None,
    page_size: Optional[int] = None,
    page_number: Optional[int] = None,
) -> PagedResponseSchema[ConversationItem]:
    """Get all conversations and filter, sort, and paginate them based on the query
    parameters.

    Parameters:
    - partition_date (str): The partition date.
    - current_user (str): The current user.
    - SK (str, optional): The secondary key of the conversation to filter.
    - conversation_start_datetime (str, optional): The conversation start datetime of the conversation to filter.
    - user_uid (str, optional): The user UID of the conversation to filter.
    - flow_type (str, optional): The flow type of the conversation to filter.
    - flow_variant_id (str, optional): The flow variant ID of the conversation to filter.
    - sort_by (str, optional): The attribute to sort by.
    - sort_direction (str, optional): The direction to sort by.
    - page_size (int, optional): The number of items per page.
    - page_number (int, optional): The current page number.

    Returns:
    - PagedResponseSchema[ConversationsWithFilters]: The paged response containing the filtered conversations and unique filters.
    """
    # Fetch all conversations with their corresponding AI states
    conversations: list[ConversationItem] = await get_conversations(partition_date=partition_date)

    unique_flow_types = set()
    unique_flow_variant_ids = set()

    for conversation in conversations:
        conversation.SK = conversation.SK.replace(ItemType.CONVERSATION.value + "#", "")
        unique_flow_types.add(conversation.flow_type)
        unique_flow_variant_ids.add(conversation.flow_variant_id)

    # Filter the conversations
    conversations = filter_conversations(
        conversation_list=conversations,
        SK=SK,
        user_uid=user_uid,
        flow_type=flow_type,
        flow_variant_id=flow_variant_id,
        conversation_start_datetime=conversation_start_datetime,
    )

    # Sort the conversations
    conversations = sort_conversations(conversations, sort_by=sort_by, sort_direction=sort_direction)

    # Paginate the conversations
    total_conversations = len(conversations)
    paginated_data = paginate(conversations, page_number, page_size)

    return PagedResponseSchema[ConversationItem](
        results=[i for i in paginated_data["data"]],
        total=total_conversations,
        next=paginated_data["next_page"],
        previous=paginated_data["prev_page"],
        filters=ConversationTableFilterItem(
            flow_type=list(unique_flow_types), flow_variant_id=list(unique_flow_variant_ids)
        ),
    )


@router.get("/conversation-daily-analytics")
async def get_conversation_analytics(
    _current_user: OIDCUser = Depends(idp.get_current_user(required_roles=[UserRoles.ADMIN_CHAT_HISTORY_VIEWER])),
) -> ConversationCount:
    """Get the daily conversation count analytics.

    Parameters:
    - current_user (str): The current user.

    Returns:
    - ConversationCount: The conversation count for current day and previous day.
    """
    current_day_conversation_count = await get_conversation_daily_count(today=True)
    previous_day_conversation_count = await get_conversation_daily_count(today=False)

    return ConversationCount(today=current_day_conversation_count, yesterday=previous_day_conversation_count)


@router.get("/conversations/{conversation_uid}")
async def get_conversation_item(
    conversation_uid: str,
    _current_user: OIDCUser = Depends(idp.get_current_user(required_roles=[UserRoles.ADMIN_CHAT_HISTORY_VIEWER])),
    message_uid: Optional[str] = None,
) -> Optional[ConversationAIStateItem]:
    """Get a conversation with AI state item by its conversation_uid and can be filtered
    to get particular AI state by by message_uid.

    Parameters:
    - conversation_uid (str): The conversation UID.
    - current_user (OIDCUser): The current user.
    - message_uid (str, optional): The message UID to filter the AI state.

    Returns:
    - ConversationAIStateItem: The conversation with AI state item.
    """
    conversation = await get_conversation_by_pk(conversation_uid=ItemType.CONVERSATION.value + "#" + conversation_uid)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation item not found")

    latest_customer_context = await get_sorted_external_conversation_customer_context(
        conversation_uid=ItemType.CONVERSATION.value + "#" + conversation_uid
    )

    if message_uid is not None:
        states = await get_conversation_ai_state_by_message_id(
            conversation_uid=ItemType.CONVERSATION.value + "#" + conversation_uid, message_uid=message_uid
        )
    else:
        states = await get_ai_conversation_states(conversation_uid=ItemType.CONVERSATION.value + "#" + conversation_uid)

    ai_state = None
    if len(states) > 0:
        ai_state = states[0]

    return ConversationAIStateItem(
        ai_state_item=ai_state, conversation_item=conversation, customer_context_item=latest_customer_context
    )


@router.get("/conversations/{conversation_uid}/callsight")
async def get_callsight_responses(
    conversation_uid: str,
    _current_user: OIDCUser = Depends(idp.get_current_user(required_roles=[UserRoles.ADMIN_CHAT_HISTORY_VIEWER])),
) -> list[CallsightItem]:
    """Get all callsight responses of a conversation by its conversation_uid.

    Parameters:
    - conversation_uid (str): The conversation UID.
    - current_user (str): The current user.

    Returns:
    - list[CallsightItem]: The list of callsight responses.
    """
    return await get_callsight_responses_for_conversation(
        conversation_pk=ItemType.CONVERSATION.value + "#" + conversation_uid
    )


@router.get("/messages/{conversation_uid}")
async def get_messages(
    conversation_uid: str,
    _current_user: OIDCUser = Depends(idp.get_current_user(required_roles=[UserRoles.ADMIN_CHAT_HISTORY_VIEWER])),
) -> list[MessageItem]:
    """Get all messages of a conversation by its conversation_uid.

    Parameters:
    - conversation_uid (str): The conversation UID.
    - current_user (str): The current user.

    Returns:
    - list[MessageItem]: The list of messages.
    """
    return await get_conversation_messages(conversation_uid=ItemType.CONVERSATION.value + "#" + conversation_uid)
