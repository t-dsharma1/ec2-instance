import re

from connectai.handlers import get_or_create_logger
from connectai.handlers.callsight.execute import run_callsight_pipeline
from connectai.handlers.internal_bus.session_bus import ConversationSessionBus
from connectai.handlers.internal_bus.shared_pubsub import PubSubKey
from connectai.handlers.llm.llm_handler import LLMHandler
from connectai.handlers.utils import string_matcher
from connectai.modules.datamodel import (
    AIStateType,
    FlowAction,
    LLMFeatures,
    OutputKey,
    Response,
    RuntimeContext,
)
from connectai.modules.state_machine.flow_config import FlowConfig
from connectai.modules.state_machine.flow_state import FlowState
from connectai.modules.state_machine.flow_supervisor.flow_supervisor import (
    FlowSupervisor,
)
from connectai.modules.state_machine.prompt import Prompt
from connectai.modules.state_machine.state import State
from genie_dao.datamodel.chatbot_db_model import ChatbotTable
from genie_dao.services import end_conversation, get_ai_conversation_states
from genie_dao.services.callsight.callsight_db_service import (
    create_callsight_response_for_conversation,
)
from genie_dao.storage.dynamodb import DynamoDBWriter

_log = get_or_create_logger(logger_name="Flow")


class Flow:
    """Finite state machine handling the current state and the transition between
    states."""

    def __init__(self, flow_config: FlowConfig):
        self.flow_graph: dict[State:FlowState] = flow_config.flow_graph
        self.flow_config = flow_config
        self.flow_supervisor = FlowSupervisor(flow_config.flow_supervisor_config)
        self.llm = LLMHandler()

    async def run(self, runtime_context: RuntimeContext, session_bus: ConversationSessionBus) -> Response:
        """Run the flow state machine.

        Takes care of the transition between states and the execution of the current
        state.
        """
        self.current_flow_state = await self._get_latest_flow_state(runtime_context)

        if runtime_context.extra_info["is_first_reach"]:
            response = await self.current_flow_state.run(runtime_context, session_bus=session_bus)
        else:
            next_state, reasoning = await self._compute_new_state(runtime_context, session_bus)
            self.next_flow_state = self._transition(
                next_state=next_state, reasoning=reasoning, runtime_context=runtime_context
            )
            flow_action: FlowAction = await self.flow_supervisor.tick(self.next_flow_state)
            response = await self._apply_action(flow_action, runtime_context, session_bus)

        return response

    async def _compute_new_state(
        self, runtime_context: RuntimeContext, session_bus: ConversationSessionBus
    ) -> tuple[State, str]:
        """Compute the next state based on the current state and the LLM model.

        Parameters
        ----------
        runtime_context: RuntimeContext
            The runtime context for the current conversation.
        Returns
        -------
        next_state: State
            The next state to transition to.
        reasoning: str
            The reasoning for the next state.
        """
        _log.info(
            f"Computing possible next states are: {[state.state_name for state in self.current_flow_state.next_states]}"
        )

        conversation_history = runtime_context.conversation.last_n_messages(1).as_prompt_messages()
        response_state = self._get_static_state_transitions(conversation_history[-1] if conversation_history else None)

        if not response_state:
            state_classifier_prompt: Prompt = self.current_flow_state.get_state_classifier_prompt()
            output_format = """{state}: {description}"""
            placeholder_values = {
                "allowed_states_name_context": [state.state_name for state in self.current_flow_state.next_states],
                "allowed_states_description_context": [
                    output_format.format(state=state.state_name, description=state.state_description)
                    for state in self.current_flow_state.next_states
                ],
                OutputKey.SUMMARY.value: runtime_context.conversation.summary,
            }
            if len(self.current_flow_state.next_states) == 1:
                # If there is only one next state, automatically transition to it
                _log.info(
                    f"Automatically transitioning to next state: {self.current_flow_state.next_states[0].state_name}"
                )
                raw_response = self.current_flow_state.next_states[0].state_name
            elif len(self.current_flow_state.next_states) == 0:
                # If there are no next states, stay in the current state
                _log.info(f"No next states found, staying in current state: {self.current_flow_state.state_name}")
                raw_response = self.current_flow_state.state_name
            else:
                # If there are multiple next states, use the state classifier
                _log.info("Using state classifier to determine next state")
                raw_response = await state_classifier_prompt.run(
                    conversation=runtime_context.conversation,
                    max_conversation_history=self.flow_config._flow_config["classifier_max_conversation_history"],
                    placeholder_values=placeholder_values,
                    session_bus=session_bus,
                    pubsub_key=PubSubKey.STATE_CLASSIFIER,
                )

            response_state = self.format_state_output(raw_response)

        next_state_name = self._get_next_state_name(response_state.state_name)
        next_state = next(state for state in self.flow_graph.keys() if state.state_name == next_state_name)

        return next_state, response_state.reasoning

    def _get_next_state_name(self, state_name: str) -> str:
        """Get the next state's name."""
        if state_name is None:
            return self.current_flow_state.state_name

        possible_next_states = self.current_flow_state.next_states
        state_names_mapping = {state.state_name: state for state in possible_next_states}

        # Match exact state name
        next_state_name = string_matcher.match_string_exact(state_name, state_names_mapping.keys())
        # Match fuzzy state name
        if next_state_name is None:
            next_state_name = string_matcher.match_string_fuzzy(
                state_name, state_names_mapping.keys(), is_case_matter=False
            )
        # Return back to same state
        if next_state_name is None:
            next_state_name = self.current_flow_state.state_name

        if next_state_name != state_name:
            _log.warning(f"State name mismatch. Expected '{state_name}', but final match was '{next_state_name}.'")

        return next_state_name

    @staticmethod
    def format_state_output(raw_response: str) -> LLMFeatures:
        # Regular expression to capture key_message, reasoning, and state
        reasoning_pattern = re.compile(r"Reasoning: [`\"]*(.+?)[`\"]*(\n|\\n|$|\.,)", re.DOTALL | re.IGNORECASE)
        key_message_pattern = re.compile(
            r"(reply by the user: [`\"]*(.+?)[`\"]*(\n|$))|(Key message: [`\"]*(.+?)[`\"]*(\n|\\n|$))",
            re.DOTALL | re.IGNORECASE,
        )

        # Search and extract the information
        reasoning_match = reasoning_pattern.search(raw_response)
        key_message_match = key_message_pattern.search(raw_response)

        # Extracting the matched groups, or setting them to None if not found
        reasoning = reasoning_match.group(1) if reasoning_match else None

        key_message = key_message_match.group(1) if key_message_match else None
        _log.info(f"State: {raw_response}, Reasoning: {reasoning}, Key Message: {key_message}")
        return LLMFeatures(state_name=raw_response, reasoning=reasoning)

    async def _get_latest_flow_state(self, runtime_context: RuntimeContext) -> FlowState:
        """Get the latest flow state for the conversation.

        If it's the first reach, set the start state.
        """
        if runtime_context.extra_info["is_first_reach"]:
            _log.info(f"First reach for conversation: {runtime_context.conversation.conversation_uid}")
            latest_state = self.flow_graph[self.flow_config.start_node]
            latest_state.enrich(self.flow_config.get_flow_config())

        else:
            _log.info(f"Getting latest state for conversation: {runtime_context.conversation.conversation_uid}")
            previous_ai_states = await get_ai_conversation_states(
                conversation_uid=runtime_context.conversation.conversation_uid
            )
            if previous_ai_states == [] or previous_ai_states is None:
                _log.warn("Warn: Couldn't find latest state, setting to initial state.")
                latest_state = self.flow_graph[self.flow_config.start_node]
                latest_state.enrich(self.flow_config.get_flow_config())
                runtime_context.extra_info["is_first_reach"] = True
            else:
                most_recent_state = previous_ai_states[0]
                for state in self.flow_graph.keys():
                    if state.state_name == most_recent_state.ai_state_name:
                        _log.info(f"Found state with name {most_recent_state.ai_state_name}")
                        latest_state = self.flow_graph[state]
                        latest_state.enrich(self.flow_config.get_flow_config())
                        # self.latest_stage_summary: str = most_recent_state.ai_conversation_summary
                        runtime_context.conversation.inject_summary(most_recent_state.ai_conversation_summary)
                _log.info(f"Error: Couldn't find state with name {most_recent_state.ai_state_name}")

        return latest_state

    def _transition(self, next_state: State, reasoning: str, runtime_context: RuntimeContext) -> FlowState:
        """Transition to the next state."""
        try:
            _log.info(f"Transitioning to next state: {next_state.state_name}")
        except AttributeError:
            _log.info(
                f"Hallucination Error: Couldn't find next state, moving to preconfigured next state in flow graph"
            )
            next_state: FlowState = self.current_flow_state.next_states[0]
            _log.info(f"Transitioning to next configured state: {next_state.state_name}")
        next_flow_state = self.flow_graph[next_state]
        next_flow_state.runtime_context = runtime_context
        next_flow_state.state_reasoning = reasoning
        next_flow_state.enrich(self.flow_config.get_flow_config())
        next_flow_state.enrich({OutputKey.SUMMARY.value: runtime_context.conversation.summary})
        return next_flow_state

    @ChatbotTable.inject_writer
    async def _apply_action(
        self,
        flow_action: FlowAction,
        runtime_context: RuntimeContext,
        session_bus: ConversationSessionBus,
        writer: DynamoDBWriter,
    ) -> Response:
        """Based on the flow supervisor's action, apply the action to the current
        state."""
        match (flow_action):
            case FlowAction.END_CONVERSATION:
                response = await self._execute_forced_end_state(runtime_context)
                await end_conversation(
                    conversation_uid=runtime_context.conversation.conversation_uid,
                )
                response.conversation_ended_flag = True

            case FlowAction.NO_ACTION:
                _log.info("No action taken")
                response = await self.next_flow_state.run(runtime_context, session_bus)
                response.conversation_ended_flag = await self._check_and_end_conversation(runtime_context)

            case _:
                _log.info("Unknown action")
                response = await self.next_flow_state.run(runtime_context, session_bus)
                response.conversation_ended_flag = await self._check_and_end_conversation(runtime_context)

        if response.conversation_ended_flag:

            async def on_chatbot_table_commit():
                await self._run_post_conversation_jobs(runtime_context)

            writer.register_on_commit_hook(on_chatbot_table_commit)

        return response

    async def _check_and_end_conversation(self, runtime_context: RuntimeContext) -> bool:
        """Check and end the conversation after execution if the next state is an end
        state."""
        if self.next_flow_state.ai_state_type == AIStateType.END_STATE.value:
            _log.info(f"Ending conversation#{runtime_context.conversation.conversation_uid}")
            await end_conversation(
                conversation_uid=runtime_context.conversation.conversation_uid,
            )
            return True
        return False

    async def _run_post_conversation_jobs(self, runtime_context: RuntimeContext) -> None:
        """Run Post-conversation Jobs:
        - Run and save Callsight pipeline response
        """

        if self.flow_config.callsight_config.enabled:
            _log.info("Running post–call analytics")
            raw_callsight_response = await run_callsight_pipeline(
                flow_id=runtime_context.extra_info["flow_type"],
                conversation_pk=runtime_context.conversation.conversation_uid,
            )
            await create_callsight_response_for_conversation(
                conversation_uid=runtime_context.conversation.conversation_uid,
                callsight_str_response=raw_callsight_response,
            )

    async def _execute_forced_end_state(self, runtime_context: RuntimeContext) -> Response:
        """Execute the forced end state."""
        self._set_state_by_type(state_type=AIStateType.FORCED_END_STATE)
        response = await self.next_flow_state.run(runtime_context)
        return response

    def _get_static_state_transitions(self, message):
        """Retrieve the static state if the message matches."""
        if message is not None:
            for key, value in self.flow_config.static_state_transitions.items():
                if message.content in value:
                    return LLMFeatures(state_name=key, reasoning="")
        return None

    def _set_state_by_type(self, state_type: AIStateType):
        """Set the current state based on the state type."""
        for state in self.flow_graph.keys():
            if state.ai_state_type == state_type.value:
                _log.info(f"Found state with type {state_type}")
                self.next_flow_state: FlowState = self.flow_graph[state]
                self.next_flow_state.enrich(self.flow_config.get_flow_config())
                return
        _log.info(f"Error: Couldn't find state with type {state_type}")

    async def run_test(
        self, start_state_name: str, runtime_context: RuntimeContext, compute_llm_response: bool = False
    ) -> Response | str:
        """This method is used to test.

        Run the flow state machine for testing purposes.
        """
        self._set_state_by_name(start_state_name)
        next_state, _ = await self._compute_new_state(runtime_context, None)

        if compute_llm_response:
            response = await self.current_flow_state.run(runtime_context, can_db_store=False)
            return response
        return next_state.state_name

    def _set_state_by_name(self, start_state_name: str):
        """This method is used to test.

        Set the current state based on the state name.
        """
        for state in self.flow_graph.keys():
            if state.state_name == start_state_name:
                _log.info(f"Found state with name {start_state_name}")
                self.current_flow_state: FlowState = self.flow_graph[state]
                self.current_flow_state.enrich(self.flow_config.get_flow_config())
                return
        _log.info(f"Error: Couldn't find state with name {start_state_name}")
