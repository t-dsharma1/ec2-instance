import re
from typing import Optional

from connectai.handlers.internal_bus.session_bus import ConversationSessionBus
from connectai.handlers.internal_bus.shared_pubsub import PubSubKey
from connectai.handlers.llm.llm_handler import LLMHandler
from connectai.modules.datamodel import (
    Conversation,
    LlmModels,
    MessageType,
    OutputKey,
    PromptTemplate,
    PromptType,
)
from genie_core.utils.logging import get_or_create_logger

_log = get_or_create_logger(logger_name="Prompt")


class Prompt:
    """Prompt with input context.

    It contains the prompt template, the type of prompt, the input context, and the
    output type.
    """

    def __init__(
        self,
        prompt_template: PromptTemplate,
        prompt_type: PromptType,
        output_key: OutputKey,
        llama_model: LlmModels,
        can_execute: bool = True,
    ):
        self.prompt_template = prompt_template
        self.output_key = output_key
        self.can_execute = can_execute
        self.prompt_type = prompt_type
        self.llama_model = llama_model
        self.llm = LLMHandler()

    def replace_placeholders(self, text: str, placeholder_values: dict) -> str:
        if text is None:
            return None
        text = self.replace_summary_placeholder(text, placeholder_values.get(OutputKey.SUMMARY.value, None))
        for key, value in placeholder_values.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text

    @staticmethod
    def replace_summary_placeholder(text: str, summary: Optional[str]) -> str:
        if not summary or summary.strip() == "":
            summary = ""
        else:
            summary = "\n--- CONVERSATION SUMMARY ---\n" + summary + "\n---\n"
        text = text.replace(f"{{{OutputKey.SUMMARY.value}}}", summary)
        return text

    async def run(
        self,
        conversation: Conversation,
        max_conversation_history: int,
        session_bus: ConversationSessionBus,
        pubsub_key: PubSubKey,
        temperature: float = None,
        top_p: float = None,
        frequency_penalty: float = None,
        placeholder_values: dict = dict(),
    ) -> str:
        llm_kwargs = {
            k: v for k, v in locals().items() if v is not None and k in ["temperature", "top_p", "frequency_penalty"]
        }
        instructions = self.replace_placeholders(self.prompt_template.instructions, placeholder_values)
        command_prompt = self.replace_placeholders(self.prompt_template.user_command, placeholder_values)

        try:
            return await self.llm.run(
                model=self.llama_model,
                instructions=instructions,
                conversation_history=conversation.last_n_messages(max_conversation_history).as_prompt_messages(),
                command_prompt=command_prompt,
                session_bus=session_bus,
                pubsub_key=pubsub_key,
                **llm_kwargs,
            )
        except Exception as e:
            raise e

    def __str__(self):
        return f"Prompt: {self.prompt_template}, Type: {self.prompt_type}, Can Execute: {self.can_execute}"


class SummaryUtilityPrompt(Prompt):
    async def run(
        self,
        conversation: Conversation,
        max_conversation_history: int,
        session_bus: ConversationSessionBus,
        pubsub_key: PubSubKey,
        temperature: float = None,
        top_p: float = None,
        frequency_penalty: float = None,
        placeholder_values: dict = dict(),
    ) -> str:
        msg_count_to_summarize = self._calc_msg_count_to_summarize(conversation)
        if msg_count_to_summarize == 0:
            return ""
        response = await super().run(
            conversation=conversation,
            session_bus=session_bus,
            pubsub_key=pubsub_key,
            max_conversation_history=msg_count_to_summarize,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            placeholder_values=placeholder_values,
        )
        response = self._post_process_response(response)
        return response

    @staticmethod
    def _calc_msg_count_to_summarize(conversation: Conversation):
        """Calculate number of messages to summarize.

        This is determined by the most recent OutputMessage that comes after an
        InputMessage or start of convo.
        """
        has_reached_output_msg = False
        for msg_count, msg in enumerate(conversation.history[::-1]):
            if has_reached_output_msg and msg.type == MessageType.input:
                return msg_count
            if msg.type == MessageType.output:
                has_reached_output_msg = True
        # reached the start of convo
        return len(conversation.history)

    @staticmethod
    def _post_process_response(text: str) -> str:
        text = text.strip().splitlines()
        intro_pattern = r".*here.*summary.*"
        if re.match(intro_pattern, text[0], re.IGNORECASE) is not None:
            text = text[1:]
        return "\n".join(text).strip()


class FlowPrompt(Prompt):
    async def run(
        self,
        conversation: Conversation,
        max_conversation_history: int,
        session_bus: ConversationSessionBus,
        pubsub_key: PubSubKey,
        temperature: float = None,
        top_p: float = None,
        frequency_penalty: float = None,
        placeholder_values: dict = dict(),
    ) -> str:
        response = await super().run(
            session_bus=session_bus,
            pubsub_key=pubsub_key,
            conversation=conversation,
            max_conversation_history=max_conversation_history,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            placeholder_values=placeholder_values,
        )
        response = self._post_process_response(response)
        return response

    @staticmethod
    def _post_process_response(text: str) -> str:
        remove = [
            "Sure! ",
            "Great! ",
            "Great, ",
            "Hello! ",
            "Hi there! ",
            "Sure, I can help you with that! ",
            "Understood! Here's my response:",
            "Sure, I understand. Here's my response:",
            "Here's my response:",
            "Sure, I'd be happy to help!",
            "Here's a possible response:",
            "Sure, here's a possible response:",
            "Sure, I can do that! Here's my response:",
        ]
        for t in remove:
            text = re.sub(f"^{t}", "", text)
        text = text[0].upper() + text[1:]
        # Remove double quotes
        text = text.strip('"')

        # remove underscores
        cleaned_string = text.replace("_", "")

        return cleaned_string


def prompt_factory(
    prompt_template: PromptTemplate,
    prompt_type: PromptType,
    output_key: OutputKey,
    llama_model: LlmModels,
    can_execute: bool = True,
):
    kwargs = {
        "prompt_template": prompt_template,
        "prompt_type": prompt_type,
        "output_key": output_key,
        "llama_model": llama_model,
        "can_execute": can_execute,
    }
    if prompt_type == PromptType.FLOW:
        return FlowPrompt(**kwargs)
    elif prompt_type == PromptType.UTILITY and output_key == OutputKey.SUMMARY:
        return SummaryUtilityPrompt(**kwargs)
    else:
        return Prompt(**kwargs)
