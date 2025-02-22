from datetime import datetime

from genie_dao.datamodel.chatbot_db_model.models import ConversationItem


def filter_conversations(
    conversation_list: list[ConversationItem],
    SK: str,
    user_uid: str,
    flow_type: str,
    flow_variant_id: str,
    conversation_start_datetime: str,
) -> list[ConversationItem]:
    """Filter the ConversationItemList based on the query parameters.

    Parameters:
    - conversation_list (list[ConversationAIStateItem]): The list of ConversationItem to filter.
    - SK (str): The secondary key of the conversation to filter.
    - user_uid (str): The user UID of the conversation to filter.
    - flow_type (str): The flow type of the conversation to filter.
    - flow_variant_id (str): The flow variant ID of the conversation to filter.
    - conversation_start_datetime (str): The conversation start datetime of the conversation to filter.

    Returns:
    - list[ConversationItem]: The filtered list of ConversationItems.
    """
    filtered_conversation_list = conversation_list
    if SK is not None:
        filtered_conversation_list = [i for i in filtered_conversation_list if SK.lower() in i.SK.lower()]
    if user_uid is not None:
        filtered_conversation_list = [i for i in filtered_conversation_list if user_uid.lower() in i.user_uid.lower()]
    if flow_type is not None:
        flow_type_list = flow_type.split(",")
        filtered_conversation_list = [i for i in filtered_conversation_list if i.flow_type in flow_type_list]
    if flow_variant_id is not None:
        flow_variant_id_list = flow_variant_id.split(",")
        filtered_conversation_list = [
            i for i in filtered_conversation_list if i.flow_variant_id in flow_variant_id_list
        ]
    if conversation_start_datetime is not None:
        date_range = conversation_start_datetime.split(",")
        start_date = datetime.strptime(date_range[0].strip(), "%Y-%m-%dT%H:%M:%S.%f")
        end_date = datetime.strptime(date_range[1].strip(), "%Y-%m-%dT%H:%M:%S.%f")
        filtered_conversation_list = [
            i
            for i in filtered_conversation_list
            if start_date <= datetime.strptime(i.conversation_start_datetime, "%Y-%m-%dT%H:%M:%S.%f") <= end_date
        ]

    return filtered_conversation_list


def sort_conversations(
    conversation_list: list[ConversationItem], sort_by: str, sort_direction: str
) -> list[ConversationItem]:
    """Sort the conversation_list based on the sort_by and sort_direction parameters.

    Parameters:
    - conversation_list (list[ConversationItem]): The list of ConversationItems to sort.
    - sort_by (str): The attribute to sort by.
    - sort_direction (str): The direction to sort by.

    Returns:
    - list[ConversationItem]: The sorted list of ConversationItems.
    """
    sorted_conversation_list = conversation_list

    if sort_by is not None and sort_direction is not None:
        sorted_conversation_list = sorted(
            sorted_conversation_list,
            key=lambda x: getattr(x, sort_by),
            reverse=sort_direction == "desc",
        )

    return sorted_conversation_list


def filter_unique_values(key: str, list_to_filter: list) -> list[str]:
    """Filter the unique values for the given key from the list_to_filter.

    Parameters:
    - key (str): The key to filter unique values.
    - list_to_filter (list): The list of conversationAIStateItems.

    Returns:
    - list[str]: The list of unique values for the given key.
    """
    return list({getattr(i, key) for i in list_to_filter if getattr(i, key) is not ["", None]})
