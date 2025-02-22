import enum
from dataclasses import dataclass

from dataclasses_json import dataclass_json

from genie_dao.datamodel._roles import Role

__all__ = ["PromptMessage", "PromptTemplate", "LlmPrompt", "PromptType", "OutputKey"]


class PromptType(enum.Enum):
    FLOW = "FLOW"  # (realtime)
    STATE_UTILITY = "STATE_UTILITY"  # 1 to 1 Mapping with the state classifier (realtime)
    UTILITY = "UTILITY"  # TONE, SENTIMENT, SUMMARY (post user message)
    CLASSIFIER = "CLASSIFIER"  # STATE CLASSIFIER


class OutputKey(enum.Enum):
    SENTIMENT = "SENTIMENT"
    TONE = "TONE"
    DATA_NEEDS = "DATA_NEEDS"
    PLAN_TYPE = "PLAN_TYPE"
    NUMBER_OF_LINES = "NUMBER_OF_LINES"
    OTTS = "OTTS"
    PIN_CODE = "PIN_CODE"
    EXISTING_SERVICES = "EXISTING_SERVICES"
    DISCUSSED_PLANS = "DISCUSSED_PLANS"
    OTHER_NEEDS = "OTHER_NEEDS"
    STATE_CLASSIFIER = "STATE_CLASSIFIER"
    FLOW = "FLOW"
    SUMMARY = "SUMMARY"


@dataclass_json
@dataclass
class PromptMessage:
    role: Role
    content: str

    def as_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass_json
@dataclass
class PromptTemplate:
    instructions: str
    example: list[PromptMessage] | None = None
    user_command: str | None = None

    @staticmethod
    def from_dict(yaml: dict) -> "PromptTemplate":
        instructions = yaml.get("instructions")
        example = [PromptMessage(role=Role(yaml.get("role")), content=ex) for ex in yaml.get("example", [])]
        user_command = yaml.get("user_command")

        return PromptTemplate(
            instructions=instructions,
            example=example,
            user_command=user_command,
        )

    @staticmethod
    def from_flow_prompt(flow_prompt) -> "PromptTemplate":
        return PromptTemplate(
            instructions=flow_prompt.instructions,
            user_command=flow_prompt.user_command,
        )

    @staticmethod
    def from_utility_prompt(utility_prompt) -> "PromptTemplate":
        return PromptTemplate(
            instructions=utility_prompt.instructions,
            example=[PromptMessage(role=ex.role, content=ex.content) for ex in utility_prompt.example],
            user_command=utility_prompt.user_command,
        )


@dataclass_json
@dataclass
class LlmPrompt:
    instructions: str
    user_command: str
    history: list[PromptMessage] | None = None

    def as_llama_request(self) -> list[dict[str, str]]:
        return (
            [PromptMessage(role="system", content=self.instructions).as_dict()]
            + [pm.as_dict() for pm in self.history]
            + [PromptMessage(role="user", content=self.user_command).as_dict()]
        )

    def as_gpt_request(self) -> list[dict[str, str]]:
        return [PromptMessage(role="system", content=self.instructions + self.user_command).as_dict()] + [
            pm.as_dict() for pm in self.history
        ]

    def as_llama2(self) -> str:
        """Format messages for Llama-2 chat models.

        The model only supports 'system', 'user' and 'assistant' roles. Message list
        must always be initialized with a ROLE = 'system'.
        """
        start_prompt = "<s>[INST] "
        end_prompt = " [/INST]"
        prompt = []
        messages = self.as_llama_request()
        for index, message in enumerate(messages):
            if message["role"] == Role.SYSTEM and index == 0:
                prompt.append(f"<<SYS>>\n{message['content']}\n<</SYS>>\n\n")
            elif message["role"] == Role.USER and messages[index - 1]["role"] != Role.USER:
                prompt.append(message["content"].strip())
            elif message["role"] == Role.USER and messages[index - 1]["role"] == Role.USER:
                prompt.append(f" [/INST] [INST] {message['content'].strip()}")
            elif message["role"] == Role.ASSISTANT:
                prompt.append(f" [/INST] {message['content'].strip()} </s><s>[INST] ")

        return start_prompt + "".join(prompt) + end_prompt

    def as_llama3(self) -> str:
        """Format messages for Llama3 instruct models."""
        prompt = []
        messages = self.as_llama_request()
        for index, message in enumerate(messages):
            if message["role"] == Role.SYSTEM and index == 0:
                prompt.append(f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>{message['content'].strip()}")
                if self.history:
                    prompt.append("--- CONVERSATION ---")
            elif message["role"] == Role.USER and index != len(messages) - 1:
                prompt.append(f"User: {message['content'].strip()}")
            elif message["role"] == Role.ASSISTANT and index != len(messages) - 1:
                prompt.append(f"Assistant: {message['content'].strip()}")
            elif message["role"] == Role.USER and index == len(messages) - 1:
                if self.history:
                    prompt.append("---")
                prompt.append(f"{message['content'].strip()}<|eot_id|><|start_header_id|>assistant<|end_header_id|>")

        return "\n".join(prompt)

    def as_gpt(self) -> list[dict[str:str]]:
        """Format messages for GPT chat.completion endpoint as a single string.

        Returns:
            list: A list of messages formatted as role: content.
        """
        messages = self.as_gpt_request()
        formatted_messages: list[dict[str:str]] = []

        for message in messages:
            role = message["role"]
            content = message["content"].strip()
            formatted_messages.append({"role": role, "content": content})
        return formatted_messages
