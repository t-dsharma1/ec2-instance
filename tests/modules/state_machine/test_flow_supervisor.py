from unittest.mock import AsyncMock, MagicMock

import pytest

from connectai.modules.datamodel import (
    AIStateType,
    Conversation,
    FlowAction,
    FlowSupervisorConfig,
    RuntimeContext,
)
from connectai.modules.state_machine.flow_supervisor.flow_supervisor import (
    FlowSupervisor,
)
from connectai.modules.state_machine.state import State
from genie_core.utils.logging import get_or_create_logger

# Mock logger
_log = get_or_create_logger(logger_name="FlowSupervisor")


@pytest.fixture
def flow_supervisor_config():
    return FlowSupervisorConfig(
        enabled=True, max_consecutive_unrelated_state_count=3, max_total_unrelated_state_count=5
    )


@pytest.fixture
def flow_supervisor(flow_supervisor_config):
    return FlowSupervisor(flow_supervisor_config)


@pytest.fixture
def current_state():
    state = MagicMock(spec=State)
    state.ai_state_type = AIStateType.GENERAL_UNRELATED_STATE.value

    # Mocking the runtime_context and its nested attributes
    runtime_context = RuntimeContext(
        conversation=Conversation(conversation_uid="test_conversation_uid"),
        extra_info={"extra_info_key": "extra_info_value"},
    )
    state.runtime_context = runtime_context

    return state


@pytest.mark.asyncio
async def test_tick_disabled_flow_supervisor(flow_supervisor_config, current_state):
    flow_supervisor_config.enabled = False
    flow_supervisor = FlowSupervisor(flow_supervisor_config)
    action = await flow_supervisor.tick(current_state)
    assert action == FlowAction.NO_ACTION


@pytest.mark.asyncio
async def test_tick_enabled_flow_supervisor(flow_supervisor, current_state):
    flow_supervisor.check_flow = AsyncMock(return_value=FlowAction.END_CONVERSATION)
    action = await flow_supervisor.tick(current_state)
    flow_supervisor.check_flow.assert_called_once_with(current_state)
    assert action == FlowAction.END_CONVERSATION


@pytest.mark.asyncio
async def test_check_flow(flow_supervisor, current_state):
    flow_supervisor.update_unrelated_state_counter = AsyncMock(return_value=FlowAction.NO_ACTION)
    action = await flow_supervisor.check_flow(current_state)
    flow_supervisor.update_unrelated_state_counter.assert_called_once_with(current_state)
    assert action == FlowAction.NO_ACTION
