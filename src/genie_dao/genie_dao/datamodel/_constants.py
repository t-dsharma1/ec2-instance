import enum
import os

__all__ = [
    "LlmModels",
    "LlmPlatformName",
    "LlmPlatformModel",
    "LLMStaticMessages",
    "LLMStaticMessages",
    "LLAMATranslationPrompt",
    "LLMDelimeters",
    "LLmModelTypes",
]


class LLmModelTypes(str, enum.Enum):
    """LLM model types supported on the language layer.

    Attributes:

        Llama2: Llama 2 models fine-tuned on chat completions.
        Llama3: Llama 3 models fine-tuned on instructions.
        GPT: OpenAI GPT models
    """

    Llama2 = "Llama2"
    Llama3 = "Llama3"
    GPT = "gpt"

    def __str__(self):
        return self.value.lower()


class LlmModels(str, enum.Enum):
    """LLM models supported on the language layer.

    Attributes:
        LLAMA2_7B: Llama 2 Chat 7 billion parameter model fine-tuned on chat completions. This is an even smaller, faster model.
        LLAMA2_13B: Llama 2 Chat 13 billion parameter model fine-tuned on chat completions. Faster and cheaper at the expense of accuracy.
        LLAMA2_70B: Llama 2 Chat 70 billion parameter model fine-tuned on chat completions. Best accuracy.
        LLAMA3_8B: Llama 3 Instruct 8 billion parameter model fine-tuned on instructions.
        LLAMA3_70B: Llama 3 Instruct 70 billion parameter model fine-tuned on instructions.
        LLAMA3_400B: Llama 3 Instruct 400 billion parameter model fine-tuned on instructions.
        GPT_4O: OpenAI GPT-4 model
        GPT_4_TURBO: OpenAI GPT-4 Turbo model
        GPT_35_TURBO: OpenAI GPT-3.5 Turbo model
        LLAMA3_1_8B: Llama 3.1 Instruct 8 billion parameter model fine-tuned on instructions.
        LLAMA3_1_70B: Llama 3.1 Instruct 70 billion parameter model fine-tuned on instructions.
    """

    LLAMA2_7B = "LLAMA2_7B"
    LLAMA2_13B = "LLAMA2_13B"
    LLAMA2_70B = "LLAMA2_70B"
    LLAMA3_8B = "LLAMA3_8B"
    LLAMA3_70B = "LLAMA3_70B"
    LLAMA3_400B = "LLAMA3_400B"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_35_TURBO = "gpt-3.5-turbo"
    LLAMA3_1_8B = "LLAMA3_1_8B"
    LLAMA3_1_70B = "LLAMA3_1_70B"

    def llm_type(self):
        """Return the llm type."""
        if self.name.startswith("LLAMA2"):
            return LLmModelTypes.Llama2
        elif self.name.startswith("LLAMA3"):
            return LLmModelTypes.Llama3
        elif self.name.startswith("GPT"):
            return LLmModelTypes.GPT
        else:
            raise ValueError(f"Model {self.name} not recognized.")


class LlmPlatformName(enum.Enum):
    ANYSCALE = "ANYSCALE"
    SAGEMAKER = "SAGEMAKER"
    BEDROCK = "BEDROCK"
    OPENAI = "OPENAI"


class LlmPlatformModel(enum.Enum):
    ANYSCALE = {
        LlmModels.LLAMA2_7B: "meta-llama/Llama-2-7b-chat-hf",
        LlmModels.LLAMA2_13B: "meta-llama/Llama-2-13b-chat-hf",
        LlmModels.LLAMA2_70B: "meta-llama/Llama-2-70b-chat-hf",
        LlmModels.LLAMA3_8B: "meta-llama/Meta-Llama-3-8B-Instruct",
        LlmModels.LLAMA3_70B: "meta-llama/Meta-Llama-3-70B-Instruct",
        LlmModels.LLAMA3_400B: None,
        LlmModels.LLAMA3_1_8B: None,
        LlmModels.LLAMA3_1_70B: None,
    }

    BEDROCK = {
        LlmModels.LLAMA2_7B: None,
        LlmModels.LLAMA2_13B: "meta.llama2-13b-chat-v1",
        LlmModels.LLAMA2_70B: "meta.llama2-70b-chat-v1",
        LlmModels.LLAMA3_8B: "meta.llama3-8b-instruct-v1:0",
        LlmModels.LLAMA3_70B: "meta.llama3-70b-instruct-v1:0",
        LlmModels.LLAMA3_400B: None,
        LlmModels.LLAMA3_1_8B: "meta.llama3-1-8b-instruct-v1:0",
        LlmModels.LLAMA3_1_70B: "meta.llama3-1-70b-instruct-v1:0",
    }
    SAGEMAKER = {
        LlmModels.LLAMA2_7B: os.getenv("SAGEMAKER_LLAMA2_7B_MODEL_NAME", None),
        LlmModels.LLAMA2_13B: os.getenv("SAGEMAKER_LLAMA2_13B_MODEL_NAME", None),
        LlmModels.LLAMA2_70B: os.getenv("SAGEMAKER_LLAMA2_70B_MODEL_NAME", None),
        LlmModels.LLAMA3_8B: os.getenv("SAGEMAKER_LLAMA3_8B_MODEL_NAME", None),
        LlmModels.LLAMA3_70B: os.getenv("SAGEMAKER_LLAMA3_70B_MODEL_NAME", None),
        LlmModels.LLAMA3_400B: os.getenv("SAGEMAKER_LLAMA3_400B_MODEL_NAME", None),
        LlmModels.LLAMA3_1_8B: os.getenv("SAGEMAKER_LLAMA3_1_8B_MODEL_NAME", None),
        LlmModels.LLAMA3_1_70B: os.getenv("SAGEMAKER_LLAMA3_1_70B_MODEL_NAME", None),
    }
    OPENAI = {
        LlmModels.GPT_4O: "gpt-4o",
        LlmModels.GPT_4_TURBO: "gpt-4-turbo",
        LlmModels.GPT_35_TURBO: "gpt-3.5-turbo",
        LlmModels.GPT_4O_MINI: "gpt-4o-mini",
    }


class LLMDelimeters(enum.Enum):
    """Chunk types to delimit parts of the generated LLM text."""

    START = "---start-stream---"
    END = "---end-stream---"


class LLMStaticMessages(enum.Enum):
    """Static messages used in the conversation flow."""

    LLM_ERROR = "I'm sorry, I'm having trouble understanding you right now."
    INPUT_SIZE_TOO_BIG = "I'm sorry, I can't process that much text at once. Please try again with a shorter message."
    LANGUAGE_RESTRICTION = (
        "Sorry, I didn't understand. I only speak in English or Hindi.\n मैं केवल अंग्रेजी या हिंदी बोलता हूं।"
    )


class LLAMATranslationPrompt(enum.Enum):
    """"""

    INSTRUCTIONS = """
    You are an expert language identification engine for telco conversations.
    Your task is to identify the language of the user input.
    You need to classify in one of the languages below.
    - English, Code: "en"
    - Hindi or Hinglish, Code: "hi"
    - Other, Code "other"
    Always respond with the language code.
    Always choose "others" when the language is not English, Hindi or Hinglish.
    It must always be one of "en", "hi" or "others", without double quotes.

    If the user input is: "Hi/hi/hi!" recognize it as the English greeting and respond with language code "en"
    If the user input is only numbers, respond with language code "en"
    """
    USER_COMMAND = """
    Identify the language from the user input: {user_input}
    Language Code:"""
