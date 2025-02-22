import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings

from genie_core.utils import env, logging

_log = logging.get_or_create_logger()


def get_package_root_path() -> Path:
    import connectai

    return Path(os.path.realpath(os.path.dirname(connectai.__file__))).parent.parent


# determine home path
# resolution order:
# 1 -> attempt using ENV value in "CONNECT_AI_HOME"
# 2 -> default to location two levels up from package home directory
ENV_CONNECTAI_HOME = os.getenv("CONNECT_AI_HOME", get_package_root_path())


class GlobalSettings(BaseSettings):
    environment: env.Environment
    home: Path
    openai_key: str = Field(alias="OPENAI_KEY")
    backend_host: Optional[str] = Field(None, alias="BACKEND_HOST")
    aws_region: Optional[str] = Field(None, alias="AWS_REGION")
    session_config_path: Path = Path("./session_config.json")
    whatsapp_business_api_url: Optional[str] = Field(None, alias="FB_WABA_URL")
    whatsapp_business_api_token: Optional[str] = Field(None, alias="FB_WABA_TOKEN")
    sagemaker_endpoint_name: Optional[str] = Field(None, alias="SAGEMAKER_ENDPOINT_NAME")
    bedrock_region: Optional[str] = Field(None, alias="BEDROCK_REGION")
    sagemaker_region: Optional[str] = Field(None, alias="SAGEMAKER_REGION")
    callsight_url: Optional[str] = Field(None, alias="CALLSIGHT_URL")
    callsight_execute_pipeline_endpoint: Optional[str] = Field(None, alias="CALLSIGHT_EXECUTE_PIPELINE_ENDPOINT")
    callsight_api_username: Optional[str] = Field(None, alias="CALLSIGHT_API_USERNAME")
    callsight_api_password: Optional[str] = Field(None, alias="CALLSIGHT_API_PASSWORD")
    dev_phone_numbers: list[str] = Field(
        [""],
        alias="DEV_PHONE_NUMBERS",
    )
    flow_configuration_cache_expiry_seconds: int = Field(
        alias="CONNECTAI_FLOW_CONFIGURATION_CACHE_EXPIRY_SECONDS", default=120
    )
    platform_base_domain: str = Field(alias="PLATFORM_BASE_DOMAIN", default="deep.atlas-platform.io")
    add_trusted_hostnames: list[str] = Field(alias="ADD_TRUSTED_HOSTNAMES", default=["*"])  # todo "*" to be replaced
    chatbot_queue_name: str = Field(alias="CHATBOT_QUEUE_NAME", default="chatbot_ingress.fifo")
    redis_host: Optional[str] = Field(None, alias="REDIS_HOST")
    redis_password: Optional[str] = Field(None, alias="REDIS_PASSWORD")

    class Config:
        extra = "ignore"


_log.info(f"Homepath is: {ENV_CONNECTAI_HOME}")

if not Path(ENV_CONNECTAI_HOME).joinpath(".env").exists():
    _log.warning(".env file not found -> please create.")

GLOBAL_SETTINGS = GlobalSettings(
    environment=env.CURRENT_ENVIRONMENT,
    home=Path(ENV_CONNECTAI_HOME),
    _env_file=Path(ENV_CONNECTAI_HOME).joinpath(".env").as_posix(),
)

_log.info(f"Global settings: {GLOBAL_SETTINGS}")
