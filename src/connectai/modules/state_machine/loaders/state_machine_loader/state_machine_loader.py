from connectai.modules.datamodel import (
    AIStateType,
    FlowCallsightConfig,
    FlowSupervisorConfig,
)
from connectai.modules.state_machine.flow import Flow
from connectai.modules.state_machine.flow_config import FlowConfig
from connectai.modules.state_machine.flow_state import FlowState
from connectai.modules.state_machine.loaders.base_yaml_loader.base_yaml_loader import (
    BaseYAMLLoader,
)
from connectai.modules.state_machine.state import State
from genie_dao.datamodel import chatbot_db_model


class StateMachineLoader(BaseYAMLLoader):
    """Class for loading a state machine from a YAML file."""

    def __init__(
        self,
        state_machine_yaml: chatbot_db_model.FlowStateMachine,
        states: list[State],
        base_config: dict,
        llm_prompts_config: dict,
        context_map: dict[str, chatbot_db_model.FlowContext],
        callsight_pipeline: dict = None,
    ):
        self.state_machine = state_machine_yaml
        self.states = states
        self.base_config = base_config
        self.llm_prompts_config = llm_prompts_config
        self.context_map = context_map
        self.callsight_pipeline = callsight_pipeline

    def load(self) -> Flow:
        flows = self.state_machine.FlowStates
        all_flows_config = self.state_machine.FlowConfig
        flow_graph: dict[State, FlowState] = {}

        for state_name in flows:
            flow_info = flows[state_name]

            flow_state = FlowState(
                state=self._get_state_by_name(state_name),
                next_states=[self._get_state_by_name(next_state) for next_state in flow_info.next_states],
            )

            flow_graph[self._get_state_by_name(state_name)] = flow_state

        all_flows_config = FlowConfig(
            start_node=self._get_first_state(),
            flow_graph=flow_graph,
            is_ai_first_message=all_flows_config.is_ai_first_message,
            static_state_transitions=all_flows_config.hard_coded_transitions,
            flow_supervisor_config=FlowSupervisorConfig(
                # enabled=all_flows_config.flow_supervisor.enabled,
                # TODO: This is a temporary fix to ensure that the flow supervisor is enabled
                enabled=False,
                max_consecutive_unrelated_state_count=int(
                    all_flows_config.flow_supervisor.max_consecutive_unrelated_state_count
                ),
                max_total_unrelated_state_count=int(all_flows_config.flow_supervisor.max_total_unrelated_state_count),
            ),
            callsight_config=FlowCallsightConfig(
                enabled=all_flows_config.callsight.enabled,
            ),
            translation_service_enabled=all_flows_config.translation_service_enabled,
            message_timeout_s=int(all_flows_config.message_timeout_s),
        )
        all_flows_config.populate_flow_default_config(
            base_config=self.base_config,
            llm_prompts_config=self.llm_prompts_config,
            context_map=self.context_map,
        )

        return Flow(all_flows_config)

    def _get_state_by_name(self, state_name: str):
        for state in self.states:
            if state.state_name == state_name:
                return state
        print("Couldn't find state with name ", state_name)
        return None

    def _get_first_state(self):
        for state in self.states:
            if state.ai_state_type == AIStateType.FIRST_STATE.value:
                return state
        print("Couldn't find first state with name")
        return None
