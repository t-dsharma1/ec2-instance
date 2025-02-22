from connectai.modules.datamodel import LlmModels, OutputKey, PromptTemplate, PromptType
from connectai.modules.state_machine.flow import State
from connectai.modules.state_machine.loaders.base_yaml_loader.base_yaml_loader import (
    BaseYAMLLoader,
)
from connectai.modules.state_machine.loaders.utility_loader.utility_loader import (
    UtilityPromptsLoader,
)
from connectai.modules.state_machine.prompt import Prompt, prompt_factory
from genie_core.utils.logging import get_or_create_logger
from genie_dao.datamodel.chatbot_db_model.models import FlowStateMetadata

logger = get_or_create_logger(logger_name="StatesLoader")


class StatesLoader(BaseYAMLLoader):
    """Class for loading states objects from a YAML file."""

    def __init__(self, states_yaml: dict[str, FlowStateMetadata], utility_prompts: UtilityPromptsLoader):
        self.states = states_yaml
        self.utility_prompts = utility_prompts

    def load(self) -> list[State]:
        states = []
        for state in self.states:
            state_name = state
            state_description = self.states[state].state_description
            state_next_goal = self.states[state].state_next_goal
            is_static_response = self.states[state].is_static_response
            ai_state_type = self.states[state].ai_state_type
            static_response = self.states[state].static_response
            state_prompts = self.states[state].state_prompts
            prompts: list[Prompt] = []
            for retriever in state_prompts.RETRIEVERS:
                match retriever.template.name:
                    case "STATE_CLASSIFIER":
                        prompts.append(
                            prompt_factory(
                                prompt_template=self.utility_prompts.STATE_CLASSIFIER,
                                prompt_type=PromptType.CLASSIFIER,
                                output_key=OutputKey.STATE_CLASSIFIER,
                                llama_model=LlmModels(retriever.template.ai_model),
                            )
                        )
                    case "TONE":
                        prompts.append(
                            prompt_factory(
                                prompt_template=self.utility_prompts.TONE,
                                prompt_type=PromptType.UTILITY,
                                output_key=OutputKey.TONE,
                                llama_model=LlmModels(retriever.template.ai_model),
                            )
                        )
                    case "SENTIMENT":
                        prompts.append(
                            prompt_factory(
                                prompt_template=self.utility_prompts.SENTIMENT,
                                prompt_type=PromptType.UTILITY,
                                output_key=OutputKey.SENTIMENT,
                                llama_model=LlmModels(retriever.template.ai_model),
                            )
                        )
                    case "DATA_NEEDS":
                        prompts.append(
                            prompt_factory(
                                prompt_template=self.utility_prompts.DATA_NEEDS,
                                prompt_type=PromptType.UTILITY,
                                output_key=OutputKey.DATA_NEEDS,
                                llama_model=LlmModels(retriever.template.ai_model),
                            )
                        )
                    case "PLAN_TYPE":
                        prompts.append(
                            prompt_factory(
                                prompt_template=self.utility_prompts.PLAN_TYPE,
                                prompt_type=PromptType.UTILITY,
                                output_key=OutputKey.PLAN_TYPE,
                                llama_model=LlmModels(retriever.template.ai_model),
                            )
                        )
                    case "NUMBER_OF_LINES":
                        prompts.append(
                            prompt_factory(
                                prompt_template=self.utility_prompts.NUMBER_OF_LINES,
                                prompt_type=PromptType.UTILITY,
                                output_key=OutputKey.NUMBER_OF_LINES,
                                llama_model=LlmModels(retriever.template.ai_model),
                            )
                        )
                    case "OTTS":
                        prompts.append(
                            prompt_factory(
                                prompt_template=self.utility_prompts.OTTS,
                                prompt_type=PromptType.UTILITY,
                                output_key=OutputKey.OTTS,
                                llama_model=LlmModels(retriever.template.ai_model),
                            )
                        )
                    case "PIN_CODE":
                        prompts.append(
                            prompt_factory(
                                prompt_template=self.utility_prompts.PIN_CODE,
                                prompt_type=PromptType.UTILITY,
                                output_key=OutputKey.PIN_CODE,
                                llama_model=LlmModels(retriever.template.ai_model),
                            )
                        )
                    case "EXISTING_SERVICES":
                        prompts.append(
                            prompt_factory(
                                prompt_template=self.utility_prompts.EXISTING_SERVICES,
                                prompt_type=PromptType.UTILITY,
                                output_key=OutputKey.EXISTING_SERVICES,
                                llama_model=LlmModels(retriever.template.ai_model),
                            )
                        )
                    case "DISCUSSED_PLANS":
                        prompts.append(
                            prompt_factory(
                                prompt_template=self.utility_prompts.DISCUSSED_PLANS,
                                prompt_type=PromptType.UTILITY,
                                output_key=OutputKey.DISCUSSED_PLANS,
                                llama_model=LlmModels(retriever.template.ai_model),
                            )
                        )
                    case "OTHER_NEEDS":
                        prompts.append(
                            prompt_factory(
                                prompt_template=self.utility_prompts.OTHER_NEEDS,
                                prompt_type=PromptType.UTILITY,
                                output_key=OutputKey.OTHER_NEEDS,
                                llama_model=LlmModels(retriever.template.ai_model),
                            )
                        )
                    case "SUMMARY":
                        prompts.append(
                            prompt_factory(
                                prompt_template=self.utility_prompts.SUMMARY,
                                prompt_type=PromptType.UTILITY,
                                output_key=OutputKey.SUMMARY,
                                llama_model=LlmModels(retriever.template.ai_model),
                            )
                        )

            try:
                flow_state_prompt_info = state_prompts.FLOW
                prompts.append(
                    prompt_factory(
                        prompt_template=PromptTemplate.from_flow_prompt(flow_state_prompt_info),
                        prompt_type=PromptType.FLOW,
                        output_key=OutputKey.FLOW,
                        llama_model=LlmModels(flow_state_prompt_info.ai_model),
                    )
                )
            except AttributeError as e:
                logger.warn(f"Skipping prompt for {state_name}. Error in loading flow state prompts {e}")

            state_obj = State(
                state_name=state_name,
                state_description=state_description,
                state_next_goal=state_next_goal,
                is_static_response=is_static_response,
                ai_state_type=ai_state_type,
                static_response=static_response,
                state_prompts=prompts,
            )

            states.append(state_obj)
        return states
