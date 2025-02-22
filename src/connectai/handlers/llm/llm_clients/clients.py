import abc
import json
from collections.abc import AsyncGenerator

import aioboto3
from aioboto3 import Session
from botocore.config import Config
from openai import AsyncOpenAI

from connectai.modules.datamodel import LLMDelimeters
from connectai.settings import GLOBAL_SETTINGS
from genie_core.utils.decorators import cache_results
from genie_core.utils.logging import get_or_create_logger

_log = get_or_create_logger(logger_name="LLMClient")


@cache_results(expiration_seconds=60 * 60)
def _make_aioboto3_session() -> Session:
    """Initializes the aioboto3 session."""
    return aioboto3.Session()


class LLMBaseClient(abc.ABC):
    """Abstract base class for all model clients."""

    def __init__(self, service_name: str):
        """Initialize the LLM client.

        Args:
            service_name: The service name.
            region_name: The region name.
        """
        self.client = None
        self.service_name = service_name

    async def __aenter__(self):
        """Enter the context manager."""
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        pass

    @abc.abstractmethod
    async def get_client(self) -> "LLMBaseClient":
        """Retrieve or create a client instance."""
        pass

    @abc.abstractmethod
    def format_request_body(
        self, prompt: str, temperature: float, top_p: float, frequency_penalty: float = None
    ) -> dict:
        """Formats the request body according to specific client requirements."""
        pass

    @abc.abstractmethod
    async def invoke(self, model: str, body: dict) -> str:
        """Invoke the LLM model specific to the client type."""
        pass

    @abc.abstractmethod
    async def invoke_streaming(self, model: str, body: dict) -> AsyncGenerator[str, None]:
        """Invoke the LLM model with streaming response specific to the client type."""
        pass

    def __str__(self) -> str:
        return f"Service Name: {self.service_name}"


class LLMAWSClient(LLMBaseClient):
    """Abstract base class for all model clients."""

    def __init__(self, service_name: str, region_name: str):
        """Initialize the LLM client.

        Args:
            service_name: The service name.
            region_name: The region name.
        """
        super().__init__(service_name=service_name)
        self.region_name = region_name

    async def __aenter__(self):
        """Enter the context manager."""
        self.client = (
            await _make_aioboto3_session()
            .client(
                service_name=self.service_name, region_name=self.region_name, config=Config(retries={"max_attempts": 1})
            )
            .__aenter__()
        )
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
            await self.client.close()

    def __str__(self) -> str:
        return f"AWS Service Name: {self.service_name}, Region Name: {self.region_name}"


class BedrockClient(LLMAWSClient):
    def __init__(self):
        super().__init__(service_name="bedrock-runtime", region_name=GLOBAL_SETTINGS.bedrock_region)

    async def get_client(self) -> LLMAWSClient:
        return self

    def format_request_body(
        self, prompt: str, temperature: float, top_p: float, frequency_penalty: float = None
    ) -> dict:
        """Formats the request body according to Bedrock requirements."""
        return {
            "prompt": prompt,
            "temperature": temperature,
            "top_p": top_p,
            # "frequency_penalty": frequency_penalty, # Bedrock doesn't support frequency penalty.
        }

    async def invoke(self, model: str, body: dict) -> str:
        """Specific invocation for Bedrock."""
        _log.info("Invoking Bedrock full response.")
        async with _make_aioboto3_session().client(
            service_name=self.service_name, region_name=self.region_name
        ) as client:
            response = await client.invoke_model(modelId=model, body=json.dumps(body))
            data = await response["body"].read()
            await client.close()
            response_body = json.loads(data)
            return response_body["generation"].strip()

    async def invoke_streaming(self, model: str, body: dict) -> AsyncGenerator[str, None]:
        """Specific invocation for Bedrock with streaming response."""
        _log.info("Invoking Bedrock with streaming response.")
        async with _make_aioboto3_session().client(
            service_name=self.service_name, region_name=self.region_name
        ) as client:
            response = await client.invoke_model_with_response_stream(modelId=model, body=json.dumps(body))
            async for event in response["body"]:
                chunk = json.loads(event["chunk"]["bytes"])
                if "generation" in chunk:
                    text = chunk["generation"]
                yield text
            # Decorator to indicate the end of the stream
            yield LLMDelimeters.END.value
            await client.close()

    def __str__(self) -> str:
        return "Bedrock"


class SageMakerClient(LLMAWSClient):
    def __init__(self):
        super().__init__(service_name="sagemaker-runtime", region_name=GLOBAL_SETTINGS.sagemaker_region)

    async def get_client(self) -> LLMAWSClient:
        return self

    def format_request_body(self, prompt: str, temperature: float, top_p: float, frequency_penalty: float = None):
        return {
            "inputs": prompt,
            "parameters": {
                "temperature": temperature,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
            },
        }

    async def invoke(self, model: str, body: dict) -> str:
        """Specific invocation for SageMaker."""
        async with _make_aioboto3_session().client(
            service_name=self.service_name, region_name=self.region_name
        ) as client:
            response = await client.invoke_endpoint(
                EndpointName=GLOBAL_SETTINGS.sagemaker_endpoint_name,
                ContentType="application/json",
                Body=json.dumps(body),
            )
            response_body = await response["Body"].read()
            await client.close()
            return json.loads(response_body)["generated_text"].strip()

    async def invoke_streaming(self, model: str, body: dict) -> AsyncGenerator[str, None]:
        raise NotImplementedError("Streaming not supported for SageMaker at the moment.")

    def __str__(self) -> str:
        return "SageMaker"


class OpenAIClient(LLMBaseClient):
    def __init__(self):
        super().__init__(service_name="OpenAI")

    async def get_client(self) -> LLMBaseClient:
        return self

    def format_request_body(
        self, prompt: str, temperature: float, top_p: float, frequency_penalty: float = None
    ) -> dict:
        """Formats the request body according to OpenAI requirements."""
        return {
            "prompt": prompt,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            # "max_tokens": 1024  # Adjust as needed
        }

    async def invoke(self, model: str, body: dict) -> str:
        """Specific invocation for OpenAI."""
        _log.info("Invoking OpenAI full response.")
        async_openai_client = AsyncOpenAI(
            api_key=GLOBAL_SETTINGS.openai_key,
        )
        chat_completion = await async_openai_client.chat.completions.create(
            messages=body["prompt"], model=model, stream=False
        )
        await async_openai_client.close()
        return chat_completion.choices[0].message.content

    async def invoke_streaming(self, model: str, body: dict) -> AsyncGenerator[str, None]:
        """Specific invocation for OpenAI with streaming response."""
        _log.info("Invoking OpenAI with streaming response.")
        async_openai_client = AsyncOpenAI(
            api_key=GLOBAL_SETTINGS.openai_key,
        )
        raw_async_response = await async_openai_client.chat.completions.create(
            messages=body["prompt"], model=model, stream=True
        )
        async for raw_event in raw_async_response:
            if raw_event.choices and len(raw_event.choices) > 0 and raw_event.choices[0].delta.content:
                yield raw_event.choices[0].delta.content
        yield LLMDelimeters.END.value
        await async_openai_client.close()

    def __str__(self) -> str:
        return "OpenAI"
