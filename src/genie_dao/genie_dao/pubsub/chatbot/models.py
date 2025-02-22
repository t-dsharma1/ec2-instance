from genie_dao.datamodel.chatbot_db_model import CallsightItem, MessageItem
from genie_dao.pubsub.models import BaseChannel, BaseMessage


class ConversationChannel(BaseChannel):
    conversation_pk: str

    def __str__(self):
        [_, conversation_id] = self.conversation_pk.split("#")
        return f"conversation:{conversation_id}"


class ChatbotMessageCreated(BaseMessage):
    name: str = "message_created"
    data: MessageItem


class ChatbotConversationEnded(BaseMessage):
    name: str = "conversation_ended"


class ChatbotPostConversationJobsFinished(BaseMessage):
    name: str = "post_conversation_jobs_finished"
    data: CallsightItem
