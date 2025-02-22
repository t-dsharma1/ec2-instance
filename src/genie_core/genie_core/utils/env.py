import enum
import os

# determine current runtime environment
# resolution order:
# 1 -> attempt using ENV value in "CONNECT_AI_ENVIRONMENT" (app deployment)
# 2 -> attempt using ENV value in "DATA_ENVIRONMENT" (Jupyterhub)
# 3 -> default to 'develop'

ENV_GENIE_ENVIRONMENT = os.getenv("DATA_ENVIRONMENT", None)


class Environment(enum.Enum):
    prod = "prod"
    preprod = "preprod"
    develop = "develop"

    @staticmethod
    def from_env() -> "Environment":
        return Environment(ENV_GENIE_ENVIRONMENT)

    def is_production(self) -> bool:
        return self == Environment.prod


CURRENT_ENVIRONMENT = Environment.from_env()
