import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

from connectai.modules.datamodel import AIStateType, FlowAction, LLMFeatures
from connectai.modules.state_machine.flow import Flow

os.environ["DATA_ENVIRONMENT"] = "develop"


class TestFlow:
    """Test the Flow class."""

    mocked_flow_config = Mock(
        start_node="start",
        flow_graph={"start": Mock()},
        flow_supervisor_config=Mock(flow_supervisor_config=Mock(enabled=False)),
        is_ai_first_message=False,
        static_state_transitions={"STATIC_STATE": ["static message"]},
    )
    flow = Flow(mocked_flow_config)

    @pytest.mark.parametrize(
        "state_classifier_response",
        [
            ("state_classifier_response_1"),
            ("state_classifier_response_2"),
            ("state_classifier_response_3"),
            ("state_classifier_response_4"),
            ("state_classifier_response_5"),
            ("state_classifier_response_6"),
            ("state_classifier_response_7"),
        ],
    )
    def test_format_state_outputs(self, state_classifier_response: dict[str, str], request) -> None:
        """Test for formatting of the state classifier response."""
        state_classifier_response = request.getfixturevalue(state_classifier_response)
        results = self.flow.format_state_output(state_classifier_response["llm_response"])
        assert results.state_name == state_classifier_response["state_name"]
        # assert results.reasoning == state_classifier_response["reasoning"]

    # flow object for testing next state name matching
    flow_for_state_name_matching = Flow(mocked_flow_config)
    next_state_names = [
        "CONVERSION",
        "OBJECTION_WITH_REASON",
        "OBJECTION_NO_REASON",
        "RELATED_CONVERSATION",
        "CUSTOMER_DEVICE_INFORMATION",
    ]
    next_states = [Mock(state_name=ele) for ele in next_state_names]
    current_flow_state = Mock(state_name="INITIAL_STATE", next_states=next_states)
    flow_for_state_name_matching.current_flow_state = current_flow_state

    @pytest.mark.parametrize(
        "state_name, expected",
        [
            ("customer device information", "CUSTOMER_DEVICE_INFORMATION"),
            ("cust device info", "CUSTOMER_DEVICE_INFORMATION"),
            ("CONVERT", "CONVERSION"),
            ("Z", "INITIAL_STATE"),
        ],
    )
    def test_get_next_state_name(self, state_name, expected):
        """Test the get next state name function."""
        assert self.flow_for_state_name_matching._get_next_state_name(state_name) == expected

    @pytest.mark.asyncio
    async def test_run_first_reach(self):
        """Test the run method for the first reach scenario."""
        runtime_context = Mock()
        runtime_context.extra_info = {"is_first_reach": True}
        runtime_context.conversation.last_n_messages.return_value.as_prompt_messages.return_value = []
        session_bus = Mock()
        session_bus.conversation_id = "test_conversation_id"
        session_bus.shared_pubsub = Mock()
        self.flow.current_flow_state = AsyncMock()
        self.flow.current_flow_state.run = AsyncMock(return_value="response")
        self.flow.flow_supervisor.tick = AsyncMock(return_value="flow_action")
        with patch.object(self.flow, "_get_latest_flow_state", AsyncMock(return_value=self.flow.current_flow_state)):
            await self.flow.run(runtime_context, session_bus)

        self.flow.flow_supervisor.tick.assert_not_called()

    @pytest.mark.asyncio
    async def test_run_not_first_reach(self):
        """Test the run method for the not first reach scenario."""
        runtime_context = Mock()
        runtime_context.extra_info = {"is_first_reach": False}
        runtime_context.conversation.last_n_messages.return_value.as_prompt_messages.return_value = ["message"]
        session_bus = Mock()
        session_bus.conversation_id = "test_conversation_id"
        session_bus.shared_pubsub = Mock()
        self.flow.current_flow_state = AsyncMock()
        self.flow._compute_new_state = AsyncMock(return_value=(Mock(), "reasoning"))
        self.flow._transition = Mock(return_value=Mock())
        self.flow.flow_supervisor.tick = AsyncMock(return_value="flow_action")
        self.flow._apply_action = AsyncMock(return_value="response")

        with patch.object(self.flow, "_get_latest_flow_state", AsyncMock(return_value=self.flow.current_flow_state)):
            await self.flow.run(runtime_context, session_bus)

        self.flow._compute_new_state.assert_called_once_with(runtime_context, session_bus)
        self.flow._transition.assert_called_once()
        self.flow.flow_supervisor.tick.assert_called_once()
        self.flow._apply_action.assert_called_once_with("flow_action", runtime_context, session_bus)

    def test_get_static_state_transitions(self):
        """Test the _get_static_state_transitions method."""
        message = Mock()
        message.content = "static message"
        result = self.flow._get_static_state_transitions(message)
        assert result == LLMFeatures(state_name="STATIC_STATE", reasoning="")

    @pytest.mark.asyncio
    async def test_execute_forced_end_state(self):
        """Test the _execute_forced_end_state method."""
        runtime_context = Mock()
        self.flow._set_state_by_type = Mock(state_type=AIStateType.FORCED_END_STATE)
        self.flow.next_flow_state = AsyncMock()
        self.flow.next_flow_state.run = AsyncMock(return_value="response")

        response = await self.flow._execute_forced_end_state(runtime_context)

        assert response == "response"

    def test_set_state_by_name(self):
        """Test the _set_state_by_name method."""
        state_name = "START_STATE"
        flow_state = Mock()
        self.flow.flow_graph = {Mock(state_name=state_name): flow_state}

        self.flow._set_state_by_name(state_name)
        assert self.flow.current_flow_state == flow_state
        flow_state.enrich.assert_called_once()

    @pytest.mark.asyncio
    async def test_apply_action_end_conversation(self):
        """Test the _apply_action method for end conversation action."""
        runtime_context = Mock()
        runtime_context.conversation.conversation_uid = "test_uid"
        response_mock = Mock(conversation_ended_flag=False)
        self.flow._execute_forced_end_state = AsyncMock(return_value=response_mock)
        self.flow.end_conversation = AsyncMock()

        flow_action = FlowAction.END_CONVERSATION
        response = await self.flow._apply_action(flow_action, runtime_context)

        assert response == "response"

    @pytest.mark.asyncio
    async def test_apply_action_no_action(self):
        """Test the _apply_action method for no action."""
        runtime_context = Mock()
        self.flow.next_flow_state = AsyncMock()
        self.flow.next_flow_state.run = AsyncMock(return_value="response")

        flow_action = FlowAction.NO_ACTION
        response = await self.flow._apply_action(flow_action, runtime_context)

        assert response == "response"

    @pytest.mark.asyncio
    async def test_apply_action_unknown(self):
        """Test the _apply_action method for unknown action."""
        runtime_context = Mock()
        self.flow.next_flow_state = AsyncMock()
        self.flow.next_flow_state.run = AsyncMock(return_value="response")

        flow_action = "UNKNOWN_ACTION"
        response = await self.flow._apply_action(flow_action, runtime_context)

        assert response == "response"
