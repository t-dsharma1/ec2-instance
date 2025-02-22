import abc

from dotenv import load_dotenv

from connectai.handlers.internal_bus.session_bus import ConversationSessionBus
from connectai.handlers.internal_bus.shared_pubsub import PubSubKey
from connectai.handlers.llm.error_strategy import ErrorRecovery, ErrorStrategy
from connectai.handlers.llm.llm_clients.clients import LLMBaseClient
from connectai.handlers.llm.platform_selector import LLMPlatformSelector
from connectai.handlers.metrics import prometheus
from connectai.modules.datamodel import (
    LlmModels,
    LLmModelTypes,
    LlmPlatformModel,
    LlmPlatformName,
    LlmPrompt,
    LLMStaticMessages,
    PromptMessage,
)
from genie_core.utils.logging import get_or_create_logger

load_dotenv()
_log = get_or_create_logger(logger_name="LLMHandler")


class LLMHandler(metaclass=abc.ABCMeta):
    """Base LLM model."""

    def __init__(
        self,
        error_strategy: ErrorStrategy = ErrorStrategy(),
    ) -> None:
        self.logger = get_or_create_logger(logger_name=self.__class__.__module__)
        self.platform_selector = LLMPlatformSelector(
            primary_model_type=LlmPlatformName.BEDROCK, fallback_model_type=LlmPlatformName.SAGEMAKER
        )
        self.error_strategy = error_strategy
        self._retry_count = 0

    async def run(
        self,
        *,
        model: LlmModels | None = None,
        instructions: str | None,
        command_prompt: str | None,
        session_bus: ConversationSessionBus,
        pubsub_key: PubSubKey,
        conversation_history: list[PromptMessage] | None = None,
        temperature: float = 0.01,
        top_p: float = 0.9,
        frequency_penalty: float = 0,
    ) -> str:
        """Run requests to LLM model.

        Args:
            model: model to be used
            instructions: Instructions and prompt to the LLM.
            user_input: User input message.
            session_bus: Shared conversation session instance.
            pubsub_key: PubSub key to resprent the message type (e.g. RESPONSE, STATE CLASSIFIER, RETRIEVER, etc.)
            conversation_history: Conversation history formatted as list of messages. Defaults to [].
            temperature: LLM fine-tuning param that controls how deterministic the reponse is. Defaults to 0.1.
            top_p: Use a lower value to ignore less probable options. Set to 0 or 1.0 to disable. Defaults to 0.9.
            frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Defaults to 0.
        Returns:
            LLM response.
        """

        prometheus.prompts_handled.inc()

        if not conversation_history:
            conversation_history = []

        self.platform_selector = LLMPlatformSelector(
            primary_model_type=LlmPlatformName.BEDROCK, fallback_model_type=LlmPlatformName.SAGEMAKER
        )
        prompt = LlmPrompt(instructions=instructions, user_command=command_prompt, history=conversation_history)
        prompt_length = 0

        match model.llm_type():
            case LLmModelTypes.Llama2:
                prompt = prompt.as_llama2()
                prompt_length = len(str(prompt).split())
            case LLmModelTypes.Llama3:
                prompt = prompt.as_llama3()
                prompt_length = len(str(prompt).split())
            case LLmModelTypes.GPT:
                prompt = prompt.as_gpt()
                prompt_length = len(" ".join([msg.get("content", "") for msg in prompt]).split())
                # GPT models are only available in OpenAI platform
                self.platform_selector.set_primary_model_type(LlmPlatformName.OPENAI)
            case _:
                self.logger.error("Invalid LLM model type.")

        while True:
            success, output = await self.run_model(
                True,
                prompt,
                model,
                temperature,
                top_p,
                frequency_penalty,
                session_bus,
                pubsub_key,
                prompt_length=prompt_length,
            )
            if success:
                break  # Successfully handled the request, break the loop

            self.logger.warn("Error invoking primary model. Determining recovery action...")
            self._retry_count += 1

            action = self.error_strategy.decide(self._retry_count)
            self.logger.info(f"Error recovery action: {action}")

            if action == ErrorRecovery.RETRY:
                continue  # Retry the primary model
            elif action == ErrorRecovery.FALLBACK:
                success, output = await self.run_model(
                    False,
                    prompt,
                    model,
                    temperature,
                    top_p,
                    frequency_penalty,
                    session_bus,
                    pubsub_key,
                    prompt_length=prompt_length,
                )
                if success:
                    break  # Successfully handled by fallback model
            else:
                if pubsub_key == PubSubKey.RESPONSE:
                    self.logger.error("Maximum retries exceeded for flow response, sending static error message.")
                    output = LLMStaticMessages.LLM_ERROR.value
                    for llm_chunk in output.split(" "):
                        session_bus.publish_chunk(message_content=llm_chunk)
                break
        return output

    async def run_model(
        self,
        use_primary: bool,
        prompt: LlmPrompt,
        model: LlmModels,
        temperature: float,
        top_p: float,
        frequency_penalty: float,
        session_bus: ConversationSessionBus,
        pubsub_key: PubSubKey,
        prompt_length: int,
    ) -> tuple[bool, str]:
        """Executes the model call, handles the primary or fallback logic.

        Returns a tuple (success, output).
        """
        try:
            llm_client = self.platform_selector.get_llm_client(primary=use_primary)
            llm_platform = self.platform_selector.get_current_client_type()
            model = LlmPlatformModel[llm_platform.value].value.get(model)
            body = llm_client.format_request_body(prompt, temperature, top_p, frequency_penalty)
            prometheus.prompt_length.labels(model=model, service=llm_client.service_name).observe(prompt_length)
            output = await handle_request(llm_client, model, body, session_bus, pubsub_key, prompt_length=prompt_length)
            return True, output  # Indicates successful handling
        except Exception as e:
            self.logger.error(f"{'Primary' if use_primary else 'Fallback'} model invocation failed: {e}")
            if "ThrottlingException" in str(e):
                prometheus.prompt_throttle_errors.inc()
            return False, None  # Indicates failure, returns None as output


async def handle_request(
    llm_client: LLMBaseClient,
    model: str,
    body: dict,
    session_bus: ConversationSessionBus,
    pubsub_key: PubSubKey,
    prompt_length: int,
) -> str:
    """Handle the request to the LLM model.

    Args:
        llm_client: The LLM client.
        model: The model to use.
        body: The request body.
        prompt_length: Number of words in the prompt

    Returns:
        The LLM response.
    """
    async with llm_client:
        with prometheus.llm_latency.labels(
            service=llm_client.service_name,
            model=str(model),
            prompt_length=_make_prompt_length_category(words=prompt_length),
        ).time():
            full_response = ""
            match pubsub_key:
                case PubSubKey.RESPONSE:
                    async for llm_chunk in llm_client.invoke_streaming(model, body):
                        session_bus.publish_chunk(message_content=llm_chunk)
                        full_response += llm_chunk
                case PubSubKey.STATE_CLASSIFIER:
                    full_response = await llm_client.invoke(model, body)
                case PubSubKey.RETRIEVER:
                    full_response = await llm_client.invoke(model, body)
                case _:
                    async for llm_chunk in llm_client.invoke_streaming(model, body):
                        session_bus.publish_chunk(message_content=llm_chunk)
                        full_response += llm_chunk
            _track_llm_response_length(service=llm_client.service_name, model=str(model), words=len(full_response))
        return full_response


def _make_prompt_length_category(words: int) -> str:
    """Produce a text label based on the amount of words.

    Args:
        words: the number of words as an integer.
    Returns:
        A formatted text label bucketing the amount of words into categories.
    """
    if words < 250:
        return "0-249"
    elif words < 500:
        return "250-499"
    elif words < 1000:
        return "500-999"
    elif words < 2000:
        return "1000-1999"
    elif words < 4000:
        return "2000-3999"
    else:
        return ">3999"


def _track_llm_response_length(service: str, model: str, words: int) -> None:
    prometheus.llm_response_length_words.labels(service=service, model=model).observe(words)
