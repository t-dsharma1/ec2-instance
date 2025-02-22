import enum

__all__ = ["AIStateType"]


class AIStateType(enum.Enum):
    """Enum for the different types of states in the state machine."""

    FIRST_STATE = "FIRST_STATE"
    INTERMEDIARY_STATE = "INTERMEDIARY_STATE"
    END_STATE = "END_STATE"
    TELCO_UNRELATED_STATE = "TELCO_UNRELATED_STATE"
    GENERAL_UNRELATED_STATE = "GENERAL_UNRELATED_STATE"
    UNRELATED_END_STATE = "UNRELATED_END_STATE"
    FORCED_END_STATE = "FORCED_END_STATE"
