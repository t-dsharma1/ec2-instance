import asyncio
import os
from subprocess import run

import click

from connectai.modules.services.db_services.flow_db_service import seed_flows
from connectai.settings import GLOBAL_SETTINGS
from genie_core.utils.logging import get_or_create_logger
from genie_dao.datamodel.chatbot_db_archive.chatbot_db_archive_table import (
    ChatbotArchiveTable,
)
from genie_dao.datamodel.chatbot_db_model.chatbot_db_table import ChatbotTable
from genie_dao.datamodel.flows_archive.flows_archive_db_table import FlowsArchiveTable
from genie_dao.datamodel.user_info.user_info_db_table import UserInfoTable

logger = get_or_create_logger(logger_name="CLI")


@click.group()
def cli():
    """Initialize cli."""


@click.group(name="start")
def start():
    """Commands to start various entrypoints."""


cli.add_command(start)


def start_fastapi_cmd() -> None:
    fastapi_command = [
        "uvicorn",
        "connectai.handlers.api.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]
    run(
        fastapi_command,
        check=True,
        cwd=GLOBAL_SETTINGS.home,
    )


@start.command(
    name="fastapi",
    help="Start the fastapi backend",
)
def start_fastapi():
    start_fastapi_cmd()


@start.command(
    name="backend",
    help="Start the FastAPI",
)
def start_backend():
    start_fastapi_cmd()


@start.command(name="dbinit", help="Bootstrapping DynamoDB tables")
def dynamodb_bootstrap():
    asyncio.run(bootstrap())


async def bootstrap():
    logger.info("Bootstrapping DynamoDB tables ...")
    await ChatbotTable.create()
    await ChatbotArchiveTable.create()
    await UserInfoTable.create()
    await FlowsArchiveTable.create()
    logger.info("Bootstrapping done.")
    logger.info("Seeding database with flows definitions")
    await seed_flows(os.path.join(os.path.dirname(__file__), "../seed/flows"))
