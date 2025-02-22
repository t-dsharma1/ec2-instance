from connectai.handlers.utils.context_graph import sort_context_topologically
from connectai.modules.datamodel import FlowCallsightConfig, FlowSupervisorConfig
from connectai.modules.state_machine.state import State
from genie_dao.datamodel import chatbot_db_model


class FlowConfig:
    """Configuration for the flow.

    Contains the start node and the flow graph and an indicator if the AI sends the
    first message.
    """

    def __init__(
        self,
        start_node: State,
        flow_graph: dict,
        flow_supervisor_config: FlowSupervisorConfig,
        callsight_config: FlowCallsightConfig,
        static_state_transitions: dict,
        message_timeout_s: int = 900,
        is_ai_first_message: bool = False,
        translation_service_enabled: bool = False,
    ):
        self.start_node = start_node
        self.flow_graph = flow_graph
        self.is_ai_first_message = is_ai_first_message
        self.flow_supervisor_config = flow_supervisor_config
        self.static_state_transitions = static_state_transitions
        self.translation_service_enabled = translation_service_enabled
        self.message_timeout_s = message_timeout_s
        self.callsight_config = callsight_config
        self._flow_config = {}

    def populate_flow_default_config(
        self,
        base_config: dict,
        llm_prompts_config: dict,
        context_map: dict[str, chatbot_db_model.FlowContext],
    ):
        # Load base config
        self._flow_config.update(base_config)
        # Load llm prompts config
        for key, value in llm_prompts_config.items():
            if isinstance(value, str):
                for config_key, config_value in base_config.items():
                    value = value.replace(f"{{{config_key}}}", str(config_value))
            self._flow_config[key] = value

        sorted_contexts = sort_context_topologically(context_map)
        self._flow_config.update({item[0]: item[1].value for item in sorted_contexts if not item[0].startswith("__")})

    def get_flow_config(self):
        return self._flow_config

    def __str__(self):
        return f"Start Node: {self.start_node}, Flow Graph: {self.flow_graph}, Flow Config: {self._flow_config}"
