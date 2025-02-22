import enum

__all__ = ["FlowAction"]


class FlowAction(enum.Enum):
    """Enum for the different types of action states of the flow supervisor."""

    NO_ACTION = "NO_ACTION"
    END_CONVERSATION = "END_CONVERSATION"
