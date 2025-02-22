from connectai.modules.datamodel import Conversation

__all__ = ["RuntimeContext"]


class RuntimeContext:
    def __init__(self, conversation: Conversation, extra_info: dict, translation_service_enabled: bool = False):
        self.extra_info = extra_info
        self.conversation = conversation
        self.translation_service_enabled = translation_service_enabled
