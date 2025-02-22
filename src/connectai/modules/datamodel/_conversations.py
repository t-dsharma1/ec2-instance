from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

from dataclasses_json import dataclass_json

from genie_dao.datamodel._customers import Customer
from genie_dao.datamodel._prompts import PromptMessage
from genie_dao.datamodel._roles import Role
from genie_dao.datamodel._translation import TranslationLanguages

from ._campaigns import Campaign
from ._features import CustomerFeatures
from ._messaging import InputMessage, MessageType, OutputMessage
from ._plans import ProductContext

__all__ = ["Conversation", "ConversationContext"]


@dataclass_json
@dataclass
class ConversationContext:
    customer_context: Optional[Customer] = None
    product_context: Optional[ProductContext] = None
    campaign_context: Optional[Campaign] = None
    external_data: Optional[dict[str, any]] = None  # Central point for external data to be passed to the flow


@dataclass_json
@dataclass
class Conversation:
    def __init__(
        self,
        conversation_uid: str,
        history: list[Union[InputMessage, OutputMessage]] = None,
        needs_and_issues: CustomerFeatures = None,
        summary: str = None,
    ):
        self.conversation_uid = conversation_uid
        self.history = history if history is not None else []
        self.needs_and_issues = needs_and_issues
        self.summary = summary
        self.current_conversation_language: str = TranslationLanguages.ENGLISH.value

    def as_prompt_messages(
        self,
    ) -> list[PromptMessage]:
        prompt_messages = [
            PromptMessage(
                role=Role.USER if message.type == MessageType.input else Role.ASSISTANT, content=message.content
            )
            for message in self.history
        ]
        return prompt_messages

    def last_n_messages(self, n: int, append_user_input: InputMessage = None) -> "Conversation":
        new_history = self.history[-n:]
        if append_user_input is not None:
            new_history.append(InputMessage(content=append_user_input.content, language=append_user_input.language))

        return Conversation(
            conversation_uid=self.conversation_uid,
            history=new_history,
            needs_and_issues=self.needs_and_issues,
            summary=self.summary,
        )

    def subset_by_type(
        self, include_input_message: bool = False, include_output_message: bool = False
    ) -> "Conversation":
        return Conversation(
            conversation_uid=self.conversation_uid,
            history=[
                m
                for m in self.history
                if (m.type == MessageType.input and include_input_message)
                or (m.type == MessageType.output and include_output_message)
            ],
            needs=self.needs_and_issues,
            summary=self.summary,
        )

    def append_to_history(self, m: Union[InputMessage, OutputMessage]) -> "Conversation":
        return Conversation(
            conversation_uid=self.conversation_uid,
            history=self.history + [m],
            needs_and_issues=self.needs_and_issues,
            summary=self.summary,
        )

    def with_replaced_history(self, replacement: list[Union[InputMessage, OutputMessage]]) -> "Conversation":
        return Conversation(
            conversation_uid=self.conversation_uid,
            history=replacement,
            needs_and_issues=self.needs_and_issues,
            summary=self.summary,
        )

    def build_new_conversation_history(self, messages: list[dict]):
        """Builds a new ENGLISH conversation history from a list of messages."""
        messages.sort(key=lambda x: x.message_sent_datetime, reverse=False)
        for msg in messages:
            if msg.message_type == MessageType.input:
                self.history.append(
                    InputMessage(
                        content=msg.message_content_en,
                        sent_at=datetime.fromisoformat(msg.message_sent_datetime),
                        type=MessageType.input,
                        language=msg.message_detected_language_code,
                    )
                )
                # The current conversation language to the last input message language
                self.current_conversation_language = msg.message_detected_language_code
            else:
                self.history.append(
                    OutputMessage(
                        msg.message_content.replace(
                            " $", r" \$"
                        ),  # message_content and not message_content_en because LLM always sends english messages
                        datetime.fromisoformat(msg.message_sent_datetime),
                        type=MessageType.output,
                    )
                )

    def build_callsight_conversation_transcript(self, messages: list[dict]) -> str:
        """Builds a new callsight-compatible conversation history from a list of
        messages."""

        self.build_new_conversation_history(messages)

        output = []
        speaker = {MessageType.input: "spk_1", MessageType.output: "spk_0"}

        for message in self.history:
            spk = speaker[message.type]
            output.append(f"{spk}: {message.content}")

        return "\n    ".join(output)

    def inject_summary(self, summary: str):
        self.summary = summary
