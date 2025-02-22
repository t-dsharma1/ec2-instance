import asyncio
from datetime import datetime, timedelta
from typing import Optional

from genie_core.utils import logging
from genie_dao.datamodel.chatbot_db_archive.chatbot_db_archive_table import (
    ChatbotArchiveTable,
)
from genie_dao.datamodel.chatbot_db_model import models
from genie_dao.datamodel.chatbot_db_model.chatbot_db_table import ChatbotTable
from genie_dao.storage import dynamodb
from genie_dao.storage.operations import scan_dynamodb_table

logger = logging.get_or_create_logger(logger_name="ArchiveManager")


async def move_data_to_archive(days_to_exclude: int = 14):
    """Archive items from ChatbotTable to ChatbotArchiveTable that are older than the
    specified number of days.

    Excludes items with flow information.
    """
    try:
        threshold_date = (datetime.now() - timedelta(days=days_to_exclude)).isoformat()

        filter_expression = "PK <> :pk AND item_created_datetime < :threshold_date"
        expression_attribute_values = {
            ":pk": str(models.FlowPK()),
            ":threshold_date": threshold_date,
        }

        logger.info(f"Scanning for conversations older than {days_to_exclude} day(s) for archival...")
        items_to_archive = await scan_dynamodb_table(
            table_name=ChatbotTable.get_table_name(),
            filter_expression=filter_expression,
            expression_attribute_values=expression_attribute_values,
        )

        if not items_to_archive:
            logger.info("No items to archive.")
            return

        async with dynamodb.DynamoDBClient() as client_db:
            archive_table = await client_db.Table(ChatbotArchiveTable.get_table_name())
            source_table = await client_db.Table(ChatbotTable.get_table_name())

            successfully_archived = []

            async with archive_table.batch_writer() as archive_batch:
                for item in items_to_archive:
                    try:
                        await archive_batch.put_item(Item=item)
                        successfully_archived.append(item)
                    except Exception as e:
                        logger.error(f"Failed to archive item {item}: {e}")

            async with source_table.batch_writer() as delete_batch:
                for item in successfully_archived:
                    try:
                        await delete_batch.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
                    except Exception as e:
                        logger.error(f"Failed to delete item {item} from source table: {e}")

            logger.info(f"Archived {len(successfully_archived)} items to {ChatbotArchiveTable.get_table_name()}.")
            return len(successfully_archived)
    except Exception as e:
        logger.error(f"Error during archival process: {e}")
        raise


async def restore_data_from_archive(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    """Restore items from ChatbotArchiveTable to ChatbotTable within the specified date
    range.

    Parameters:
    - start_date (datetime, optional): The start date of the range. Items from this date onward will be restored.
    - end_date (datetime, optional): The end date of the range. Items up to this date will be restored.
      If both are None, all items are restored.
    """
    try:
        filter_expression = []
        expression_attribute_values = {}

        if start_date:
            filter_expression.append("item_created_datetime >= :start_date")
            expression_attribute_values[":start_date"] = start_date.isoformat()
        if end_date:
            filter_expression.append("item_created_datetime <= :end_date")
            expression_attribute_values[":end_date"] = end_date.isoformat()

        filter_expression_str = " AND ".join(filter_expression) if filter_expression else None

        logger.info(f"Scanning archive table for items within the specified date range: {start_date} to {end_date}...")
        items_to_restore = await scan_dynamodb_table(
            table_name=ChatbotArchiveTable.get_table_name(),
            filter_expression=filter_expression_str,
            expression_attribute_values=expression_attribute_values,
        )

        if not items_to_restore:
            logger.info("No items to restore.")
            return

        async with dynamodb.DynamoDBClient() as client_db:
            main_table = await client_db.Table(ChatbotTable.get_table_name())

            async with main_table.batch_writer() as restore_batch:
                for item in items_to_restore:
                    try:
                        await restore_batch.put_item(Item=item)
                    except Exception as e:
                        logger.error(f"Failed to restore item {item}: {e}")

            logger.info(
                f"Restored {len(items_to_restore)} items from {ChatbotArchiveTable.get_table_name()} to {ChatbotTable.get_table_name()}."
            )
            return len(items_to_restore)
    except Exception as e:
        logger.error(f"Error during restoration process: {e}")
        raise


async def periodic_task(days_to_exclude: int = 14):
    """Periodic task to archive conversation data older than the specified number of
    days."""

    # TODO: Move archival task to a DAG runner in airflow or triggering this from a lamda or some process outside the runtime
    while True:
        logger.info(f"Starting periodic archive task at {datetime.now()}")
        try:
            await move_data_to_archive(days_to_exclude)
        except Exception as e:
            logger.error(f"Error during periodic archive task: {e}")

        await asyncio.sleep(days_to_exclude * 24 * 60 * 60)
