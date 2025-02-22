import contextlib
import contextvars
import dataclasses
import functools
import os
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Iterable
from contextlib import AsyncContextDecorator
from enum import Enum
from typing import Any, Callable, Optional

import aioboto3
from aioboto3 import Session
from aioboto3.dynamodb import table as dynamodb_table

from genie_core.utils import env
from genie_core.utils.decorators import cache_results
from genie_core.utils.logging import get_or_create_logger

_log = get_or_create_logger(logger_name="dynamodb")

AWS_REGION = os.getenv("AWS_REGION", None)

_client_kwargs_from_settings = {}
if AWS_REGION is not None:
    _client_kwargs_from_settings["region_name"] = AWS_REGION


@cache_results(expiration_seconds=60 * 60)
def _make_aioboto3_session() -> Session:
    """Initializes the aioboto3 session."""
    return aioboto3.Session()


class DynamoDBClient:
    def __init__(self):
        self.client = None

    async def __aenter__(self):
        self.client = await _make_aioboto3_session().resource("dynamodb", **_client_kwargs_from_settings).__aenter__()
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)


class DynamoDataType(str, Enum):
    string = "S"
    number = "N"
    binary = "B"
    bool = "BOOL"
    null = "NULL"
    map = "M"
    list = "L"
    string_set = "SS"
    number_set = "NS"
    binary_set = "BS"


class DynamoKeyType(str, Enum):
    HASH = "HASH"
    RANGE = "RANGE"


class DynamoAttributeProjectionType(str, Enum):
    ALL = "ALL"
    KEYS_ONLY = "KEYS_ONLY"
    INCLUDE = "INCLUDE"


@dataclasses.dataclass
class DynamoTableAttribute:
    name: str
    type: DynamoDataType

    def as_definition_dict(self) -> dict[str, str]:
        return {"AttributeName": self.name, "AttributeType": self.type.value}


@dataclasses.dataclass
class DynamoTableKeyAttribute:
    name: str
    type: DynamoKeyType

    def as_definition_dict(self) -> dict[str, str]:
        return {"AttributeName": self.name, "KeyType": self.type.value}


@dataclasses.dataclass
class DynamoTableGlobalSecondaryIndex:
    name: str
    key_schema: list[DynamoTableKeyAttribute]
    projection_type: DynamoAttributeProjectionType
    projection_non_key_attributes: list[str] | None = None
    provisioned_throughput_read: int = 10
    provisioned_throughput_write: int = 10

    def make_projection_dict(self) -> dict[str, Any]:
        if self.projection_type == DynamoAttributeProjectionType.INCLUDE:
            return {
                "ProjectionType": self.projection_type.value,
                "NonKeyAttributes": self.projection_non_key_attributes,
            }
        else:
            return {"ProjectionType": self.projection_type.value}

    def as_definition_dict(self) -> dict[str, Any]:
        return {
            "IndexName": self.name,
            "KeySchema": [k.as_definition_dict() for k in self.key_schema],
            "Projection": self.make_projection_dict(),
        }


class BatchWriteTransaction(AsyncContextDecorator):
    class CustomBatchWriter(dynamodb_table.BatchWriter):
        async def _flush_if_needed(self):
            pass

    def __init__(self, outer_cls):
        self.outer_cls = outer_cls
        self.writer: Optional[DynamoDBBatchWriter] = None

    async def __aenter__(self):
        self.stack = await contextlib.AsyncExitStack().__aenter__()
        try:
            client_db = await self.stack.enter_async_context(DynamoDBClient())
            table = await client_db.Table(self.outer_cls.get_table_name())
            batch_writer = await self.stack.enter_async_context(
                BatchWriteTransaction.CustomBatchWriter(
                    table.name, table.meta.client, flush_amount=25, overwrite_by_pkeys=None, on_exit_loop_sleep=0
                )
            )
            self.writer = DynamoDBBatchWriter(batch_writer)
            self.outer_cls.writer_ctx.set(self.writer)
        except BaseException:
            await self.stack.aclose()
            raise
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.commit()
        self.outer_cls.writer_ctx.set(None)
        return await self.stack.__aexit__(exc_type, exc_val, exc_tb)

    def rollback(self):
        if self.writer is not None:
            self.writer.rollback()

    async def commit(self):
        if self.writer is not None:
            await self.writer.commit()


class DynamoDBWriter(ABC):
    def __init__(self):
        self._on_commit_callbacks: list[Callable[[], Awaitable]] = []

    @abstractmethod
    async def put_item(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete_item(self, *args, **kwargs):
        raise NotImplementedError

    async def _on_commit(self):
        for callback in self._on_commit_callbacks:
            await callback()
        self._on_commit_callbacks = []

    def register_on_commit_hook(self, callback: Callable[[], Awaitable]):
        self._on_commit_callbacks.append(callback)


class DynamoDBTableWriter(DynamoDBWriter):
    def __init__(self, table: dynamodb_table.TableResource):
        super().__init__()
        self._table = table

    async def put_item(self, *args, **kwargs):
        await self._table.put_item(*args, **kwargs)
        await self._on_commit()

    async def delete_item(self, *args, **kwargs):
        await self._table.delete_item(*args, **kwargs)


class DynamoDBBatchWriter(DynamoDBWriter):
    def __init__(self, batch_writer: dynamodb_table.BatchWriter):
        super().__init__()
        self._batch_writer = batch_writer

    async def put_item(self, *args, **kwargs):
        await self._batch_writer.put_item(*args, **kwargs)

    async def delete_item(self, *args, **kwargs):
        await self._batch_writer.delete_item(*args, **kwargs)

    async def commit(self):
        _log.info(f"Commiting {len(self._batch_writer._items_buffer)} items.")
        while self._batch_writer._items_buffer:
            await self._batch_writer._flush()
        await self._on_commit()

    def rollback(self):
        _log.info(f"Rolling back {len(self._batch_writer._items_buffer)} items.")
        self._batch_writer._items_buffer = []
        self._on_commit_callbacks = []


@dataclasses.dataclass
class DynamoDBTable(ABC):
    name: str
    attributes: list[DynamoTableAttribute]
    key_schema: list[DynamoTableKeyAttribute]
    global_secondary_indexes: list[DynamoTableGlobalSecondaryIndex] | None = None
    provisioned_throughput_read: int | None = None  # can be None for on-demand
    provisioned_throughput_write: int | None = None  # can be None for on-demand
    billing_mode: str = "PAY_PER_REQUEST"  # Default to PAY_PER_REQUEST (on demand), can be also set to "PROVISIONED"
    stream_enabled: bool = False
    stream_view_type: str | None = None
    writer_ctx: Optional[contextvars.ContextVar[Optional[DynamoDBWriter]]] = None

    @classmethod
    def get_table_name(cls) -> str:
        return env.CURRENT_ENVIRONMENT.value.lower() + "_" + cls.name

    @classmethod
    async def create(cls, exists_okay: bool = True) -> None:
        table_name = cls.get_table_name()
        params = {
            "TableName": table_name,
            "KeySchema": [k.as_definition_dict() for k in cls.key_schema],
            "AttributeDefinitions": [a.as_definition_dict() for a in cls.attributes],
            "BillingMode": cls.billing_mode,
        }

        if cls.billing_mode == "PROVISIONED":
            params.update(
                {
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": cls.provisioned_throughput_read,
                        "WriteCapacityUnits": cls.provisioned_throughput_write,
                    }
                }
            )

        if cls.global_secondary_indexes is not None:
            gsi_definitions = [gsi.as_definition_dict() for gsi in cls.global_secondary_indexes]
            for gsi in gsi_definitions:
                if cls.billing_mode == "PROVISIONED":
                    gsi.update(
                        {
                            "ProvisionedThroughput": {
                                "ReadCapacityUnits": cls.provisioned_throughput_read,
                                "WriteCapacityUnits": cls.provisioned_throughput_write,
                            }
                        }
                    )
            params.update({"GlobalSecondaryIndexes": gsi_definitions})

        if cls.stream_enabled and cls.stream_view_type is not None:
            params.update(
                {
                    "StreamSpecification": {
                        "StreamEnabled": cls.stream_enabled,
                        "StreamViewType": cls.stream_view_type,
                    }
                }
            )

        _log.info(f"Creating DynamoDB table: {table_name}...")
        try:
            async with DynamoDBClient() as client:
                table = await client.create_table(**params)
                await table.wait_until_exists()
        except Exception as e:
            if exists_okay and ("Cannot create preexisting table" in str(e) or "Table already exists:" in str(e)):
                _log.info("Already exists – skipping create,")
            else:
                _log.info("Error creating DynamoDB table. Request was:")
                _log.info(params)
                raise e
        _log.info(f"Created.")

    @classmethod
    def batch_write_transaction(cls) -> BatchWriteTransaction:
        """Function decorator that creates a DynamoDB table resource in batch mode.

        All functions wrapped in
        `inject_writer` and run in its context will acquire this batch writer instance instead of the regular
        TableResource. This way all calls to put_item will be run in batch at the end of the execution, not immediately.
        """

        return BatchWriteTransaction(outer_cls=cls)

    @classmethod
    def inject_writer(cls, fn):
        """Function decorator that acquires a batch writer instance, if present, or
        creates a DynamoDB table resource.

        If you want to use a batch writer remember to wrap an ancestor function in `batch_write_transaction`.
        """

        @functools.wraps(fn)
        async def _inject_writer(*args, **kwargs):
            writer = cls.writer_ctx.get()
            if writer is not None:
                kwargs.setdefault("writer", writer)
                return await fn(*args, **kwargs)

            async with DynamoDBClient() as client_db:
                table = await client_db.Table(cls.get_table_name())
                kwargs.setdefault("writer", DynamoDBTableWriter(table=table))
                return await fn(*args, **kwargs)

        return _inject_writer


async def bootstrap(tables: Iterable[type[DynamoDBTable]]) -> None:
    for t in tables:
        await t.create()
