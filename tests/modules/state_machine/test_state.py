# tests/test_state.py
from unittest.mock import AsyncMock, Mock, patch

import pytest

from connectai.handlers.internal_bus.session_bus import ConversationSessionBus
from connectai.handlers.internal_bus.shared_pubsub import PublicPubSub
from connectai.modules.datamodel import OutputKey, PromptType, RuntimeContext
from connectai.modules.state_machine.prompt import Prompt
from connectai.modules.state_machine.state import State


@pytest.fixture
def mock_runtime_context():
    conversation = Mock()
    conversation.inject_summary = Mock()
    conversation.conversation_uid = "test_uid"
    conversation.current_conversation_language = "EN"
    conversation.extra_info = {"user_message_uid": "123"}

    runtime_context = Mock(spec=RuntimeContext)
    runtime_context.conversation = conversation
    runtime_context.extra_info = {}
    runtime_context.translation_service_enabled = False
    return runtime_context


@pytest.fixture
def mock_prompts():
    prompt1 = Mock(spec=Prompt)
    prompt1.prompt_type = PromptType.UTILITY
    prompt1.output_key = OutputKey.SUMMARY
    prompt1.can_execute = True
    prompt1.run = AsyncMock(return_value="summary result")

    prompt2 = Mock(spec=Prompt)
    prompt2.prompt_type = PromptType.FLOW
    prompt2.output_key = OutputKey.FLOW
    prompt2.can_execute = True
    prompt2.run = AsyncMock(return_value="flow result")

    return [prompt1, prompt2]


@pytest.fixture
def state(mock_prompts):
    state = State(
        state_name="test_state",
        state_description="A test state",
        state_next_goal="next_goal",
        state_prompts=mock_prompts,
        ai_state_type="test_type",
        static_response="",
        is_static_response=False,
    )
    state._state_context = {}
    state._state_context["utility_max_conversation_history"] = 10
    state._state_context["utility_temperature"] = 0.01
    state._state_context["utility_top_p"] = 0.01
    state._state_context["flow_top_p"] = 0.01
    state._state_context["utility_frequency_penalty"] = 0.0
    state._state_context["flow_frequency_penalty"] = 0.0
    state._state_context["flow_temperature"] = 5
    state._state_context["flow_max_conversation_history"] = 5
    state._state_context["summary"] = "summary result"

    return state


@patch("connectai.modules.state_machine.state.create_message", new_callable=AsyncMock)
@patch("connectai.modules.state_machine.state.create_ai_state_for_conversation", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_run_state(mock_create_ai_state, mock_create_message, state, mock_runtime_context):
    mock_create_message.return_value = Mock(message_uid="msg_uid", message_content_en="flow result")

    state._populate_dynamic_runtime_context(runtime_context=mock_runtime_context, can_db_store=True)
    response = await state.run(
        runtime_context=mock_runtime_context,
        can_db_store=True,
        session_bus=ConversationSessionBus(shared_pubsub=PublicPubSub()),
    )

    assert response.llm_response == "flow result"
    assert response.llm_features.state_name == "test_state"
    assert response.dialogue_features.language == "EN"
    assert response.customer_features.data_needs is None  # Assuming no data_needs_response in this test
    assert state._state_context[OutputKey.FLOW.value] == "flow result"

    mock_create_message.assert_called_once()
    mock_create_ai_state.assert_called_once()


@pytest.mark.asyncio
async def test_run_prompt_and_save(state, mock_prompts, mock_runtime_context):
    prompt = mock_prompts[0]
    session_bus = Mock()
    session_bus.conversation_id = "test_conversation_id"
    session_bus.shared_pubsub = Mock()
    pubsub_key = Mock()
    state._populate_dynamic_runtime_context(runtime_context=mock_runtime_context, can_db_store=True)
    await state._run_prompt_and_save(prompt=prompt, pubsub_key=pubsub_key, session_bus=session_bus)

    assert state._state_context["summary"] == "summary result"
    prompt.run.assert_called_once()


def test_retrieve_prompts_by_type(state, mock_prompts):
    utility_prompts = state._retrieve_prompts_by_type(PromptType.UTILITY)
    assert utility_prompts == [mock_prompts[0]]

    flow_prompts = state._retrieve_prompts_by_type(PromptType.FLOW)
    assert flow_prompts == [mock_prompts[1]]


# @pytest.mark.asyncio
# async def test_populate_state_context_utility_values(state, mock_prompts, mock_runtime_context):
#     state._populate_dynamic_runtime_context(runtime_context=mock_runtime_context, can_db_store=False)
#     await state._populate_state_context_utility_values()

#     assert state._state_context["summary"] == "summary result"
#     mock_prompts[0].run.assert_called_once()


@pytest.mark.asyncio
async def test_populate_state_context_flow_value(state, mock_prompts, mock_runtime_context):
    state._populate_dynamic_runtime_context(runtime_context=mock_runtime_context, can_db_store=False)
    session_bus = Mock()
    session_bus.conversation_id = "test_conversation_id"
    session_bus.shared_pubsub = Mock()
    await state._populate_state_context_flow_value(session_bus)

    assert state._state_context[OutputKey.FLOW.value] == "flow result"
    mock_prompts[1].run.assert_called_once()


def test_format_static_response_and_save(state):
    state.is_static_response = True
    # mock session_bus object
    session_bus = Mock()
    session_bus.conversation_id = "test_conversation_id"
    session_bus.shared_pubsub = Mock()
    state.static_response = "Static response with {summary}"
    state._state_context["summary"] = "summary result"

    state._format_static_response_and_save(session_bus)
    assert state._state_context[OutputKey.FLOW.value] == "Static response with summary result"


def test_get_state_classifier_prompt(state, mock_prompts):
    mock_prompts[0].output_key = OutputKey.STATE_CLASSIFIER
    classifier_prompt = state.get_state_classifier_prompt()
    assert classifier_prompt == mock_prompts[0]


def test_enrich(state):
    new_context = {"new_key": "new_value"}
    state.enrich(new_context)
    assert state._state_context["new_key"] == "new_value"


def test_populate_dynamic_runtime_context(state, mock_runtime_context):
    state._populate_dynamic_runtime_context(runtime_context=mock_runtime_context, can_db_store=True)
    assert state.runtime_context == mock_runtime_context


@patch("connectai.modules.state_machine.state.create_message", new_callable=AsyncMock)
@patch("connectai.modules.state_machine.state.create_ai_state_for_conversation", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_save_ai_state(mock_create_ai_state, mock_create_message, state, mock_runtime_context):
    state._populate_dynamic_runtime_context(runtime_context=mock_runtime_context, can_db_store=True)
    state._state_context[OutputKey.FLOW.value] = "flow result"

    mock_create_message.return_value = Mock(message_uid="msg_uid", message_content_en="flow result")

    response = await state._save_ai_state()

    assert response.llm_response == "flow result"
    assert response.llm_features.state_name == "test_state"
    assert response.dialogue_features.language == "EN"
    mock_create_message.assert_called_once()
    mock_create_ai_state.assert_called_once()
