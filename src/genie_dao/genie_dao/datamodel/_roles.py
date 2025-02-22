from dataclasses_json import dataclass_json


@dataclass_json
class Role:
    """Role of the messenger for interacting with Llama models.
    Public Anyscale endpoints follow the chat completation formatting normally used on OpenAI.
    https://app.endpoints.anyscale.com/docs

    See https://platform.openai.com/docs/guides/text-generation/chat-completions-api for more information.

    Attributes:
        SYSTEM: Instructions to the LLM. Most of the prompt engineering happens here.
        USER: User message(s)
        ASSISTANT: LLM response(s)
    """

    SYSTEM: str = "system"
    USER: str = "user"
    ASSISTANT: str = "assistant"
