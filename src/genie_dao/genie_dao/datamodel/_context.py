import enum

__all__ = ["ContextType", "ContextVariableType"]


class ContextType(str, enum.Enum):
    CUSTOMER_DATA = "customer_data"
    PRODUCT_DATA = "product_data"
    SALES_FLOW_STRATEGY = "sales_flow_strategy"


class ContextVariableType(str, enum.Enum):
    API = "api"
    USER_DEFINED = "user_defined"
    UTILITIES_OUTPUT = "utilities_output"
