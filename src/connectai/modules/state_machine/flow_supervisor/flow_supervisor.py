from connectai.modules.datamodel import AIStateType, FlowAction, FlowSupervisorConfig
from genie_core.utils.logging import get_or_create_logger
from genie_dao.datamodel.chatbot_db_model.models import AIStateItem, FlowSupervisorItem
from genie_dao.services import (
    create_flow_supervisor_state,
    get_ai_conversation_states,
    get_flow_supervisor_states,
)

_log = get_or_create_logger(logger_name="FlowSupervisor")


class FlowSupervisor:
    """Supervisor of the flow. Makes sure that the flow is running correctly.

    Current responsibilities:
    - For a flow execution, the flow supervisor will end the conversation if:
        - The flow has been in ai_state_type unrelated state multiple times in a row.
        - The flow has been in total multiple times in state_tpe unrelated state.
    """

    def __init__(self, flow_supervisor_config: FlowSupervisorConfig):
        """Initialize the flow supervisor."""
        self.enabled = flow_supervisor_config.enabled

        self.max_consecutive_unrelated_state_count = flow_supervisor_config.max_consecutive_unrelated_state_count
        self.max_total_unrelated_state_count = flow_supervisor_config.max_total_unrelated_state_count

        self.total_unrelated_state_count = 0
        self.consecutive_unrelated_state_count = 0
        _log.info(f"Flow supervisor config: {flow_supervisor_config}")

    async def tick(self, current_state) -> FlowAction:
        _log.info("tick: Checking if flow supervisor is enabled")
        if not self.enabled:
            return FlowAction.NO_ACTION

        _log.info("tick: Flow supervisor is enabled, calling check_flow")
        return await self.check_flow(current_state)

    async def check_flow(self, current_state) -> FlowAction:
        _log.info("check_flow: Calling update_unrelated_state_counter")
        return await self.update_unrelated_state_counter(current_state)

    async def update_unrelated_state_counter(self, current_state) -> FlowAction:
        _log.info("update_unrelated_state_counter: Starting update process")

        previous_ai_states: AIStateItem = await get_ai_conversation_states(
            current_state.runtime_context.conversation.conversation_uid
        )
        _log.info(f"update_unrelated_state_counter: Retrieved previous AI states: {previous_ai_states}")

        if len(previous_ai_states) <= 1:
            _log.info("update_unrelated_state_counter: No previous AI states found")
            previous_ai_state = current_state
        else:
            _log.info("update_unrelated_state_counter: Previous AI states found")
            previous_ai_state = previous_ai_states[1]

        latest_flow_supervisor_item: FlowSupervisorItem = (
            await get_flow_supervisor_states(current_state.runtime_context.conversation.conversation_uid)
        )[0]
        _log.info(
            f"update_unrelated_state_counter: Retrieved latest flow supervisor item: {latest_flow_supervisor_item}"
        )

        self.total_unrelated_state_count = latest_flow_supervisor_item.total_unrelated_state_count
        self.consecutive_unrelated_state_count = latest_flow_supervisor_item.consecutive_unrelated_state_count

        _log.info(f"Current state type: {current_state.ai_state_type}")
        _log.info(f"Previous state type: {previous_ai_state.ai_state_type}")

        if current_state.ai_state_type == AIStateType.GENERAL_UNRELATED_STATE.value:
            _log.info("Unrelated state detected")
            self.total_unrelated_state_count += 1

            if previous_ai_state.ai_state_type == AIStateType.GENERAL_UNRELATED_STATE.value:
                _log.info("Consecutive unrelated state detected")
                self.consecutive_unrelated_state_count += 1
            else:
                _log.info("Starting consecutive unrelated state counter")
                self.consecutive_unrelated_state_count = 1
        else:
            _log.info("Resetting consecutive unrelated state counter")
            self.consecutive_unrelated_state_count = 0

        if (
            self.consecutive_unrelated_state_count >= self.max_consecutive_unrelated_state_count
            or self.total_unrelated_state_count >= self.max_total_unrelated_state_count
        ):
            _log.info("Ending conversation due to unrelated state")
            flow_supervisor_action = FlowAction.END_CONVERSATION
        else:
            flow_supervisor_action = FlowAction.NO_ACTION

        _log.info(f"Total unrelated state count: {self.total_unrelated_state_count}")
        _log.info(f"Consecutive unrelated state count: {self.consecutive_unrelated_state_count}")

        _log.info("Creating new flow supervisor state")
        await create_flow_supervisor_state(
            current_state.runtime_context.conversation.conversation_uid,
            total_unrelated_state_count=self.total_unrelated_state_count,
            consecutive_unrelated_state_count=self.consecutive_unrelated_state_count,
        )
        _log.info("update_unrelated_state_counter: Completed update process")
        return flow_supervisor_action
