from unittest.mock import Mock

import pytest

from connectai.handlers.internal_bus.shared_pubsub import PubSubKey
from connectai.modules.datamodel import (
    Conversation,
    InputMessage,
    LlmModels,
    MessageType,
    OutputKey,
    PromptType,
)
from connectai.modules.state_machine.loaders.flow_factory import FlowFactory
from connectai.modules.state_machine.prompt import FlowPrompt, prompt_factory


class TestSummaryUtilityPrompt:
    """Test the summary utility prompt class."""

    utility_prompts = FlowFactory(flow_type="")._load_utility_prompts()
    prompt = prompt_factory(
        prompt_template=utility_prompts.SUMMARY,
        prompt_type=PromptType.UTILITY,
        output_key=OutputKey.SUMMARY,
        llama_model=LlmModels.LLAMA3_8B,
    )

    @pytest.mark.parametrize(
        "summarizer_response",
        [
            ("summarizer_response_1"),
            ("summarizer_response_2"),
        ],
    )
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_summarizer_output(self, summarizer_response: dict[str, str], request) -> None:
        """Test outputs of summarizer utility."""
        summarizer_response = request.getfixturevalue(summarizer_response)
        conversation = Conversation(conversation_uid="none", history=summarizer_response["conversation_history"])
        summary = await self.prompt.run(
            pubsub_key=PubSubKey.RESPONSE,
            conversation=conversation,
            max_conversation_history=3,
            temperature=0.01,
            top_p=0.0001,
            frequency_penalty=0,
        )
        summary = summary.lower()
        assert all(ele not in summary for ele in summarizer_response["must_not_contain"])
        assert all(ele in summary for ele in summarizer_response["must_contain"])
        assert len(summary.split("\n")) <= summarizer_response["max_line_count"], summary

    @pytest.mark.asyncio
    async def test_empty_conversation(self) -> None:
        """Test summarizer with an empty conversation history."""
        conversation = Conversation(conversation_uid="none", history=[])
        session_bus = Mock()
        session_bus.conversation_id = "test_conversation_id"
        session_bus.shared_pubsub = Mock()
        summary = await self.prompt.run(
            session_bus=session_bus,
            pubsub_key=PubSubKey.RESPONSE,
            conversation=conversation,
            max_conversation_history=3,
            temperature=0.01,
            top_p=0.0001,
            frequency_penalty=0,
        )
        assert summary == ""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_single_message_conversation(self) -> None:
        """Test summarizer with a single message in the conversation history."""
        conversation = Conversation(
            conversation_uid="none",
            history=[InputMessage(content="Hello", type=MessageType.input)],
        )
        summary = await self.prompt.run(
            pubsub_key=PubSubKey.RESPONSE,
            conversation=conversation,
            max_conversation_history=1,
            temperature=0.01,
            top_p=0.0001,
            frequency_penalty=0,
        )
        assert "hello" in summary.lower()

    @pytest.mark.asyncio
    async def test_multiple_output_messages(self) -> None:
        """Test summarizer with multiple output messages in the conversation history."""
        conversation = Conversation(
            conversation_uid="none",
            history=[
                InputMessage(content="Hello", type=MessageType.input),
                InputMessage(content="Hi, how can I help you?", type=MessageType.output),
                InputMessage(content="I need assistance with my account.", type=MessageType.input),
                InputMessage(content="Sure, I can help with that.", type=MessageType.output),
            ],
        )
        session_bus = Mock()
        session_bus.conversation_id = "test_conversation_id"
        session_bus.shared_pubsub = Mock()
        summary = await self.prompt.run(
            session_bus=session_bus,
            pubsub_key=PubSubKey.RESPONSE,
            conversation=conversation,
            max_conversation_history=4,
            temperature=0.01,
            top_p=0.0001,
            frequency_penalty=0,
        )
        assert summary is not None

    @pytest.mark.asyncio
    async def test_summary_with_placeholders(self) -> None:
        """Test summarizer with placeholders in the prompt template."""
        conversation = Conversation(
            conversation_uid="none",
            history=[
                InputMessage(content="Hello", type=MessageType.input),
                InputMessage(content="Hi, how can I help you?", type=MessageType.output),
            ],
        )
        session_bus = Mock()
        session_bus.conversation_id = "test_conversation_id"
        session_bus.shared_pubsub = Mock()
        summary = await self.prompt.run(
            session_bus=session_bus,
            pubsub_key=PubSubKey.RESPONSE,
            conversation=conversation,
            max_conversation_history=2,
            temperature=0.01,
            top_p=0.0001,
            frequency_penalty=0,
            placeholder_values={"CUSTOMER_NAME": "John"},
        )
        assert summary is not None

    def test_replace_placeholders(self):
        """Test the replace_placeholders method."""
        template = "Hello, {CUSTOMER_NAME}. How can I assist you today?"
        placeholder_values = {"CUSTOMER_NAME": "Alice"}
        result = self.prompt.replace_placeholders(template, placeholder_values)
        assert result == "Hello, Alice. How can I assist you today?"

    def test_replace_summary_placeholder(self):
        """Test the replace_summary_placeholder method."""
        text = "Summary: {SUMMARY}"
        summary = "This is a test summary."
        result = self.prompt.replace_summary_placeholder(text, summary)
        expected_result = "Summary: \n--- CONVERSATION SUMMARY ---\nThis is a test summary.\n---\n"
        assert result == expected_result

    def test_replace_summary_placeholder_empty(self):
        """Test the replace_summary_placeholder method with an empty summary."""
        text = "Summary: {SUMMARY}"
        summary = ""
        result = self.prompt.replace_summary_placeholder(text, summary)
        expected_result = "Summary: "
        assert result == expected_result

    @pytest.mark.parametrize(
        "input_text, expected_output",
        [
            ("Great! This is another test response.", "This is another test response."),
            ("Hello! Summary: This is yet another test response.", "Summary: This is yet another test response."),
        ],
    )
    def test_flow_prompt_post_process_response(self, input_text, expected_output):
        """Test the _post_process_response method in FlowPrompt."""
        cleaned_response = FlowPrompt._post_process_response(input_text)
        assert cleaned_response == expected_output
