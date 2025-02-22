from connectai.modules.state_machine.state import State


class FlowState(State):
    """State with next states.

    It contains the next states that can be reached from the current state.
    """

    def __init__(self, state: State, next_states: list[State]):
        super().__init__(
            state_name=state.state_name,
            state_prompts=state.state_prompts,
            state_description=state.state_description,
            state_next_goal=state.state_next_goal,
            static_response=state.static_response,
            is_static_response=state.is_static_response,
            ai_state_type=state.ai_state_type,
        )
        self.next_states = next_states

    def __str__(self):
        return super().__str__() + f" Next states: {self.next_states}"
