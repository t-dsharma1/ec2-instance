import pytest
from dotenv import load_dotenv

from connectai.handlers.llm.llm_handler import LLMHandler
from connectai.modules.datamodel import LlmModels


class TestLLMHandler:
    """Test the LLM handler for API requests to AnyScale, Bedrock and Sagemaker."""

    @pytest.mark.parametrize(
        "model",
        [LlmModels.LLAMA3_8B, LlmModels.LLAMA3_70B],
        ids=[LlmModels.LLAMA3_8B, LlmModels.LLAMA3_70B],
    )
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_bedrock_service(self, model: LlmModels):
        """Test Bedrock API is correctly setup."""
        load_dotenv()

        bedrock_handler = LLMHandler()
        response = await bedrock_handler.run(
            model=model,
            instructions="You are a helpful assistant.",
            command_prompt="Say 'Test' and no more. Do not add punctuaction either.",
        )

        assert response == "Test"
