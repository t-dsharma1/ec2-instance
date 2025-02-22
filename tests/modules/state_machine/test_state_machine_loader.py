from unittest.mock import AsyncMock, Mock

import pytest

from connectai.modules.datamodel import ContextType, OutputKey, PromptType
from connectai.modules.state_machine.flow import Flow
from connectai.modules.state_machine.flow_state import FlowState
from connectai.modules.state_machine.loaders.state_machine_loader.state_machine_loader import (
    StateMachineLoader,
)
from connectai.modules.state_machine.prompt import Prompt
from connectai.modules.state_machine.state import State
from genie_dao.datamodel import chatbot_db_model


@pytest.fixture
def state_machine_yaml():
    mock_yaml = Mock(spec=chatbot_db_model.FlowStateMachine)
    mock_yaml.FlowStates = {
        "state 1": Mock(next_states=["state 2"]),
        "state 2": Mock(next_states=[]),
    }
    mock_yaml.FlowConfig = Mock(
        is_ai_first_message=True,
        start_node="state1",
        flow_supervisor=Mock(
            enabled=True,
            max_consecutive_unrelated_state_count="3",
            max_total_unrelated_state_count="5",
        ),
        hard_coded_transitions={"state1": "state2"},
        translation_service_enabled=True,
        message_timeout_s="60",
    )
    return mock_yaml


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
def states(mock_prompts):
    return [
        State(
            state_name="state 1",
            state_description="A test state",
            state_next_goal="next_goal",
            state_prompts=mock_prompts,
            ai_state_type="test_type",
            static_response="",
            is_static_response=False,
        ),
        State(
            state_name="state 2",
            state_description="A test state",
            state_next_goal="next_goal",
            state_prompts=mock_prompts,
            ai_state_type="test_type",
            static_response="",
            is_static_response=False,
        ),
    ]


@pytest.fixture
def base_config():
    return {"some_base_config": "value"}


@pytest.fixture
def llm_prompts_config():
    return {"some_llm_prompts_config": "value"}


@pytest.fixture
def context_map():
    return {
        "context1": chatbot_db_model.FlowContext(
            value="value",
            context_type=ContextType.CUSTOMER_DATA,
        )
    }


@pytest.fixture
def state_machine_loader(state_machine_yaml, states, base_config, llm_prompts_config, context_map):
    return StateMachineLoader(state_machine_yaml, states, base_config, llm_prompts_config, context_map)


def test_load(state_machine_loader, state_machine_yaml, states):
    state_machine_yaml.FlowStates = {
        states[0].state_name: FlowState(states[0], states),
    }

    # state_machine_yaml.FlowConfig = FlowConfig(
    #     is_ai_first_message=True,
    #     start_node=states[0],
    #     flow_graph={states[0]: FlowState(states[0], states)},
    #     flow_supervisor_config=FlowSupervisorConfig(
    #         enabled=True,
    #         max_consecutive_unrelated_state_count=3,
    #         max_total_unrelated_state_count=5,
    #     ),
    #     static_state_transitions= {"state 1": "state 2"},
    #     translation_service_enabled=True,
    #     message_timeout_s="60",
    # )
    state_machine_yaml.FlowConfig = Mock(
        is_ai_first_message=True,
        start_node=states[0],
        flow_supervisor=Mock(
            enabled=True,
            max_consecutive_unrelated_state_count="3",
            max_total_unrelated_state_count="5",
        ),
        hard_coded_transitions={"state1": "state2"},
        translation_service_enabled=True,
        message_timeout_s="60",
    )

    flow = state_machine_loader.load()

    assert isinstance(flow, Flow)
    assert flow.flow_config.start_node is None
    assert flow.flow_config.translation_service_enabled is True
    assert flow.flow_config.message_timeout_s == 60
