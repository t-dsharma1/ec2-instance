__all__ = ["FlowCallsightConfig"]


class FlowCallsightConfig:
    def __init__(self, enabled: bool):
        self.enabled = enabled

    def __str__(self):
        return f"FlowCallsightConfig(enabled={self.enabled})"
