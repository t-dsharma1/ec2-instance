from unittest.mock import create_autospec

import pytest

from connectai.modules.datamodel import AIStateType
from connectai.modules.state_machine.flow import State
from connectai.modules.state_machine.loaders.states_loader.states_loader import (
    StatesLoader,
)
from connectai.modules.state_machine.loaders.utility_loader.utility_loader import (
    UtilityPromptsLoader,
)
from genie_dao.datamodel.chatbot_db_model.models import (
    FlowStateMetadata,
    FlowStatePrompts,
    FlowStateRetriever,
    FlowStateRetrieverTemplate,
)


# Mock dependencies
@pytest.fixture
def utility_prompts_loader():
    mock_loader = create_autospec(UtilityPromptsLoader)
    mock_loader.STATE_CLASSIFIER = "mock_classifier_template"
    mock_loader.TONE = "mock_tone_template"
    mock_loader.SENTIMENT = "mock_sentiment_template"
    mock_loader.DATA_NEEDS = "mock_data_needs_template"
    mock_loader.PLAN_TYPE = "mock_plan_type_template"
    mock_loader.NUMBER_OF_LINES = "mock_number_of_lines_template"
    mock_loader.OTTS = "mock_otts_template"
    mock_loader.PIN_CODE = "mock_pin_code_template"
    mock_loader.EXISTING_SERVICES = "mock_existing_services_template"
    mock_loader.DISCUSSED_PLANS = "mock_discussed_plans_template"
    mock_loader.OTHER_NEEDS = "mock_other_needs_template"
    mock_loader.SUMMARY = "mock_summary_template"
    return mock_loader


@pytest.fixture
def states_yaml():
    return {
        "state1": FlowStateMetadata(
            state_description="Description of state1",
            state_next_goal="next_goal_1",
            is_static_response=False,
            ai_state_type=AIStateType.FIRST_STATE,
            static_response=None,
            state_prompts=FlowStatePrompts(
                RETRIEVERS=[
                    FlowStateRetriever(
                        template=FlowStateRetrieverTemplate(name="STATE_CLASSIFIER", ai_model="LLAMA3_8B")
                    ),
                    FlowStateRetriever(template=FlowStateRetrieverTemplate(name="TONE", ai_model="LLAMA3_8B")),
                    FlowStateRetriever(template=FlowStateRetrieverTemplate(name="SENTIMENT", ai_model="LLAMA3_8B")),
                    FlowStateRetriever(template=FlowStateRetrieverTemplate(name="DATA_NEEDS", ai_model="LLAMA3_8B")),
                    FlowStateRetriever(template=FlowStateRetrieverTemplate(name="PLAN_TYPE", ai_model="LLAMA3_8B")),
                    FlowStateRetriever(
                        template=FlowStateRetrieverTemplate(name="NUMBER_OF_LINES", ai_model="LLAMA3_8B")
                    ),
                    FlowStateRetriever(template=FlowStateRetrieverTemplate(name="OTTS", ai_model="LLAMA3_8B")),
                    FlowStateRetriever(template=FlowStateRetrieverTemplate(name="PIN_CODE", ai_model="LLAMA3_8B")),
                    FlowStateRetriever(
                        template=FlowStateRetrieverTemplate(name="EXISTING_SERVICES", ai_model="LLAMA3_8B")
                    ),
                    FlowStateRetriever(
                        template=FlowStateRetrieverTemplate(name="DISCUSSED_PLANS", ai_model="LLAMA3_8B")
                    ),
                    FlowStateRetriever(template=FlowStateRetrieverTemplate(name="OTHER_NEEDS", ai_model="LLAMA3_8B")),
                    FlowStateRetriever(template=FlowStateRetrieverTemplate(name="SUMMARY", ai_model="LLAMA3_8B")),
                ],
                FLOW=None,
            ),
        ),
        "state2": FlowStateMetadata(
            state_description="Description of state2",
            state_next_goal="next_goal_2",
            is_static_response=True,
            ai_state_type=AIStateType.INTERMEDIARY_STATE,
            static_response="static_response_2",
            state_prompts=FlowStatePrompts(
                RETRIEVERS=[
                    FlowStateRetriever(
                        template=FlowStateRetrieverTemplate(name="STATE_CLASSIFIER", ai_model="LLAMA3_8B")
                    ),
                    FlowStateRetriever(template=FlowStateRetrieverTemplate(name="TONE", ai_model="LLAMA3_8B")),
                    FlowStateRetriever(template=FlowStateRetrieverTemplate(name="SENTIMENT", ai_model="LLAMA3_8B")),
                    FlowStateRetriever(template=FlowStateRetrieverTemplate(name="DATA_NEEDS", ai_model="LLAMA3_8B")),
                    FlowStateRetriever(template=FlowStateRetrieverTemplate(name="PLAN_TYPE", ai_model="LLAMA3_8B")),
                    FlowStateRetriever(
                        template=FlowStateRetrieverTemplate(name="NUMBER_OF_LINES", ai_model="LLAMA3_8B")
                    ),
                    FlowStateRetriever(template=FlowStateRetrieverTemplate(name="OTTS", ai_model="LLAMA3_8B")),
                    FlowStateRetriever(template=FlowStateRetrieverTemplate(name="PIN_CODE", ai_model="LLAMA3_8B")),
                    FlowStateRetriever(
                        template=FlowStateRetrieverTemplate(name="EXISTING_SERVICES", ai_model="LLAMA3_8B")
                    ),
                    FlowStateRetriever(
                        template=FlowStateRetrieverTemplate(name="DISCUSSED_PLANS", ai_model="LLAMA3_8B")
                    ),
                    FlowStateRetriever(template=FlowStateRetrieverTemplate(name="OTHER_NEEDS", ai_model="LLAMA3_8B")),
                    FlowStateRetriever(template=FlowStateRetrieverTemplate(name="SUMMARY", ai_model="LLAMA3_8B")),
                ],
                FLOW=None,
            ),
        ),
    }


# Test StatesLoader initialization
def test_states_loader_init(states_yaml, utility_prompts_loader):
    loader = StatesLoader(states_yaml, utility_prompts_loader)
    assert loader.states == states_yaml
    assert loader.utility_prompts == utility_prompts_loader


# Test StatesLoader load method
def test_states_loader_load(states_yaml, utility_prompts_loader):
    loader = StatesLoader(states_yaml, utility_prompts_loader)
    states = loader.load()
    assert len(states) == 2
    assert isinstance(states[0], State)
    assert states[0].state_name == "state1"
    assert states[1].state_name == "state2"

    # Verify properties of state1
    state1 = states[0]
    assert state1.state_description == "Description of state1"
    assert state1.state_next_goal == "next_goal_1"
    assert not state1.is_static_response
    assert state1.ai_state_type == AIStateType.FIRST_STATE.value
    assert state1.static_response is None

    # Verify properties of state2
    state2 = states[1]
    assert state2.state_description == "Description of state2"
    assert state2.state_next_goal == "next_goal_2"
    assert state2.is_static_response
    assert state2.ai_state_type == AIStateType.INTERMEDIARY_STATE.value
    assert state2.static_response == "static_response_2"
