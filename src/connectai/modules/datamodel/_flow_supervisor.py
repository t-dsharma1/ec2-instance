__all__ = ["FlowSupervisorConfig"]


class FlowSupervisorConfig:
    def __init__(self, enabled: bool, max_consecutive_unrelated_state_count: int, max_total_unrelated_state_count: int):
        self.enabled = enabled
        self.max_consecutive_unrelated_state_count = max_consecutive_unrelated_state_count
        self.max_total_unrelated_state_count = max_total_unrelated_state_count

    def __str__(self):
        return f"FlowSupervisorConfig(enabled={self.enabled}, max_consecutive_unrelated_state_count={self.max_consecutive_unrelated_state_count}, max_total_unrelated_state_count={self.max_total_unrelated_state_count})"
