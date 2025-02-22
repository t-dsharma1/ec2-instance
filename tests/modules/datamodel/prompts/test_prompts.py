import pytest

from connectai.modules.datamodel import LlmPrompt


class TestPrompts:
    """Test the LLM handler for API requests to AnyScale, Bedrock and Sagemaker."""

    @pytest.mark.parametrize(
        "llama_prompt,prompt_as_request",
        [
            ("no_history_conversation", "no_history_conversation_as_request"),
            ("user_start_conversation", "user_start_conversation_as_request"),
            ("assistant_start_conversation", "assistant_start_conversation_as_request"),
            ("user_start_conversation_double", "user_start_conversation_double_as_request"),
            ("assistant_start_conversation_double", "assistant_start_conversation_double_as_request"),
        ],
    )
    def test_prompt_as_request(self, llama_prompt: LlmPrompt, prompt_as_request: list[dict[str, str]], request) -> None:
        """Test formatting prompt as requests."""
        assert request.getfixturevalue(llama_prompt).as_llama_request() == request.getfixturevalue(prompt_as_request)

    @pytest.mark.parametrize(
        "llama_prompt,prompt_as_llama2",
        [
            ("no_history_conversation", "no_history_conversation_as_llama2"),
            ("user_start_conversation", "user_start_conversation_as_llama2"),
            ("assistant_start_conversation", "assistant_start_conversation_as_llama2"),
            ("user_start_conversation_double", "user_start_conversation_double_as_llama2"),
            ("assistant_start_conversation_double", "assistant_start_conversation_double_as_llama2"),
        ],
    )
    def test_prompt_as_llama2(self, llama_prompt: LlmPrompt, prompt_as_llama2: str, request) -> None:
        """Test formatting prompt as requests."""
        assert request.getfixturevalue(llama_prompt).as_llama2() == request.getfixturevalue(prompt_as_llama2)

    @pytest.mark.parametrize(
        "llama_prompt,prompt_as_llama3",
        [
            ("no_history_conversation", "no_history_conversation_as_llama3"),
            ("user_start_conversation", "user_start_conversation_as_llama3"),
            ("assistant_start_conversation", "assistant_start_conversation_as_llama3"),
            ("user_start_conversation_double", "user_start_conversation_double_as_llama3"),
            ("assistant_start_conversation_double", "assistant_start_conversation_double_as_llama3"),
        ],
    )
    def test_prompt_as_llama3(self, llama_prompt: LlmPrompt, prompt_as_llama3: str, request) -> None:
        """Test formatting prompt as requests."""
        assert request.getfixturevalue(llama_prompt).as_llama3() == request.getfixturevalue(prompt_as_llama3)
