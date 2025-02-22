from connectai.handlers.llm.llm_clients.clients import (
    BedrockClient,
    LLMBaseClient,
    OpenAIClient,
    SageMakerClient,
)
from connectai.modules.datamodel import LlmPlatformName
from genie_core.utils.logging import get_or_create_logger

_log = get_or_create_logger(logger_name="LLMPlatformSelector")


class LLMPlatformSelector:
    """Selects the primary and fallback LLM platform."""

    def __init__(self, primary_model_type: LlmPlatformName, fallback_model_type: LlmPlatformName | None = None):
        """Create a new instance of LLMPlatformSelector if it doesn't exist, otherwise
        return the existing instance.

        Args:
            primary_model_type: The primary LLM platform.
            fallback_model_type: The fallback LLM platform.
        """
        self.primary_model_type = primary_model_type
        self.fallback_model_type = fallback_model_type
        self.model_clients = {
            LlmPlatformName.BEDROCK: BedrockClient(),
            LlmPlatformName.SAGEMAKER: SageMakerClient(),
            LlmPlatformName.OPENAI: OpenAIClient(),
        }
        self.current_client = self.model_clients[primary_model_type]

    def get_llm_client(self, primary: bool = True) -> LLMBaseClient:
        """Get the LLM client.

        Args:
            primary: Whether to use the primary model or the fallback model.

        Returns:
            LLMBaseClient: The LLM Base client.
        """
        client = (
            self.model_clients[self.primary_model_type] if primary else self.model_clients[self.fallback_model_type]
        )
        self.current_client = client

        return client

    def set_primary_model_type(self, primary_model_type: LlmPlatformName) -> None:
        """Set the primary model type.

        Args:
            primary_model_type: The primary model type.
        """
        self.primary_model_type = primary_model_type
        self.current_client = self.model_clients[primary_model_type]

    def get_current_client_type(self) -> LlmPlatformName:
        """Get the current client type.

        Returns:
            LlmPlatformName: The current client type.
        """
        return (
            self.primary_model_type
            if self.current_client == self.model_clients[self.primary_model_type]
            else self.fallback_model_type
        )

    def __str__(self) -> str:
        return f"Primary Model: {self.primary_model_type}, Fallback Model: {self.fallback_model_type}"
