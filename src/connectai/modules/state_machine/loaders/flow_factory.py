import json

from connectai.modules.state_machine.loaders.base_yaml_loader.base_yaml_loader import (
    BaseYAMLLoader,
)
from connectai.modules.state_machine.loaders.state_machine_loader.state_machine_loader import (
    StateMachineLoader,
)
from connectai.modules.state_machine.loaders.states_loader.states_loader import (
    StatesLoader,
)
from connectai.modules.state_machine.loaders.utility_loader.utility_loader import (
    UtilityPromptsLoader,
)
from connectai.settings import GLOBAL_SETTINGS
from genie_core.utils.decorators import cache_results
from genie_core.utils.logging import get_or_create_logger
from genie_dao.datamodel import chatbot_db_model
from genie_dao.services.flow.flow_db_service import get_latest_flow_variants_metadata

logger = get_or_create_logger(logger_name="FlowFactory")


class FlowFactory:
    """Factory class for creating a flow.

    - Loads the base config, llm prompts config, dynamic context, static context, utility prompts, states and state machine.
    - Creates a flow object.
    """

    def __init__(self, flow_type: str, flow_variant_number: int = 0, base_path: str = "../../../../seed") -> None:
        self.flow_type = flow_type
        self.flow_variant_number = flow_variant_number
        self.BASE_PATH = base_path
        self.FLOW_PATH = f"flows/{flow_type}/0"  # FIXME: Version 0 is tested by default
        self.CONFIG_PATH = f"{self.BASE_PATH}/{self.FLOW_PATH}/config"
        self.CONTEXT_MAP_PATH = f"{self.BASE_PATH}/{self.FLOW_PATH}/context_map"
        self.STATES_PATH = f"{self.BASE_PATH}/{self.FLOW_PATH}/states"
        self.STATE_MACHINE_PATH = f"{self.BASE_PATH}/{self.FLOW_PATH}/state_machine"
        self.SHARED_PATH = f"{self.BASE_PATH}/shared"
        self.CALLSIGHT_PATH = f"{self.BASE_PATH}/{self.FLOW_PATH}/callsight"

    def create_flow_from_local(self):
        """Create a flow object from the local seed files."""
        base_config_loader = BaseYAMLLoader(f"{self.CONFIG_PATH}/base_config.yaml")
        base_config = base_config_loader.load()

        llm_prompts_config_loader = BaseYAMLLoader(f"{self.CONFIG_PATH}/config.yaml")
        llm_prompts_config = llm_prompts_config_loader.load()

        context_map_loader = BaseYAMLLoader(f"{self.CONTEXT_MAP_PATH}/context_map.yaml")
        context_map = context_map_loader.load()
        context_map_obj: dict[str, chatbot_db_model.FlowContext] = {
            key: chatbot_db_model.FlowContext(**item) for key, item in context_map.items()
        }

        utility_prompts = self._load_utility_prompts()

        states_yaml_loader = BaseYAMLLoader(f"{self.STATES_PATH}/states.yaml")
        states_yaml = states_yaml_loader.load()
        states_obj: dict[str, chatbot_db_model.FlowStateMetadata] = {
            key: chatbot_db_model.FlowStateMetadata(**value) for key, value in states_yaml.items()
        }

        states_yaml_loader = StatesLoader(states_yaml=states_obj, utility_prompts=utility_prompts)
        states = states_yaml_loader.load()

        state_machine_yaml_loader = BaseYAMLLoader(f"{self.STATE_MACHINE_PATH}/state_machine_flow.yaml")
        state_machine_yaml = state_machine_yaml_loader.load()
        state_machine_obj: chatbot_db_model.FlowStateMachine = chatbot_db_model.FlowStateMachine(**state_machine_yaml)

        callsight_pipeline_loader = BaseYAMLLoader(f"{self.CALLSIGHT_PATH}/pipeline.yaml")
        callsight_pipeline = callsight_pipeline_loader.load()

        flow_loader = StateMachineLoader(
            state_machine_yaml=state_machine_obj,
            states=states,
            base_config=base_config,
            llm_prompts_config=llm_prompts_config,
            context_map=context_map_obj,
            callsight_pipeline=callsight_pipeline,
        )
        return flow_loader.load()

    def _load_utility_prompts(self) -> UtilityPromptsLoader:
        """Load utility prompts."""
        utility_prompts_yaml_loader = BaseYAMLLoader(f"{self.SHARED_PATH}/utility_prompts.yaml")
        utility_prompts_yaml = utility_prompts_yaml_loader.load()
        utility_prompts_obj: dict[str, chatbot_db_model.FlowStateUtilityPrompt] = {
            key: chatbot_db_model.FlowStateUtilityPrompt(**value) for key, value in utility_prompts_yaml.items()
        }

        utility_prompts = UtilityPromptsLoader(utility_prompts=utility_prompts_obj)
        utility_prompts.load()
        return utility_prompts

    @cache_results(expiration_seconds=GLOBAL_SETTINGS.flow_configuration_cache_expiry_seconds)
    async def create_flow_from_db(self):
        """Create a flow object from the db."""

        flow_type_variants = await get_latest_flow_variants_metadata(self.flow_type)
        flow_data = flow_type_variants[self.flow_variant_number]

        base_config = json.loads(flow_data.flow_base_config)
        llm_prompts_config = flow_data.flow_config_llm_prompts
        context_map = flow_data.flow_context_map
        utility_prompts_yaml = flow_data.flow_utility_prompts
        state_machine_yaml = flow_data.flow_state_machine
        states_yaml = flow_data.flow_states
        callsight_pipeline = flow_data.callsight_pipeline

        utility_prompts = UtilityPromptsLoader(utility_prompts=utility_prompts_yaml)
        utility_prompts.load()

        states_yaml_loader = StatesLoader(states_yaml=states_yaml, utility_prompts=utility_prompts)
        states = states_yaml_loader.load()

        flow_loader = StateMachineLoader(
            state_machine_yaml=state_machine_yaml,
            states=states,
            base_config=base_config,
            llm_prompts_config=llm_prompts_config,
            context_map=context_map,
            callsight_pipeline=callsight_pipeline,
        )
        return flow_loader.load()
