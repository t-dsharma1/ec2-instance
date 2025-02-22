import abc
import asyncio
import json
import os
import pathlib
import sys
from datetime import datetime

import boto3
import pandas as pd
from openai import OpenAI

from connectai.evaluation import RESULTS_SUBDIR, ROOT_DIR, TEST_CASE_PATH
from connectai.evaluation.factory.test_factory import TestCase, TestFactory
from connectai.handlers import get_or_create_logger
from connectai.modules.datamodel import Conversation

from .metrics import BUSINESS_LOGIC, FAITHFULLNESS, RAI, RELEVANCE, Assessment, Metric

DEFAULT_RESULTS_PATH = ROOT_DIR / RESULTS_SUBDIR

from dotenv import load_dotenv

load_dotenv()


class BaseEvaluator(metaclass=abc.ABCMeta):
    """Base evaluation class."""

    client = OpenAI(
        api_key=os.getenv("EVALUATION_OPENAI_API_KEY"),
        organization=os.getenv("EVALUATION_OPENAI_ORGANIZATION"),
        base_url=os.getenv("EVALUATION_OPENAI_BASE_URL"),
    )

    def __init__(self, *, test_case_path: str | None = None, export_filename: str) -> None:
        self.test_case_path = test_case_path
        self.test_cases = self._build_test_cases(test_case_path)
        self.export_file_path = self._create_export_path(export_filename)
        self.logger = get_or_create_logger(logger_name=self.__class__.__module__)
        self.s3_client = boto3.client("s3")

    @classmethod
    def get_test_case_path(cls):
        module = sys.modules[cls.__module__]
        path = pathlib.Path(module.__file__).parent / TEST_CASE_PATH
        return path

    def _create_export_path(self, file_name: str) -> pathlib.Path:
        path = DEFAULT_RESULTS_PATH / file_name
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _build_test_cases(self, test_case_path) -> list[TestCase]:
        tf = TestFactory()
        if test_case_path is None:
            self.test_case_path = self.get_test_case_path()
        with open(self.test_case_path) as file:
            test_cases = json.load(file)
            return [item for test in test_cases for item in tf.build(**test)]

    def format_conversation(self, conversation_history: Conversation) -> str:
        conversation = []
        for x in conversation_history.as_prompt_messages():
            conversation.append(f"{x.role.upper()}: {x.content}")
        return "\n----\n".join(conversation)

    def export(self, results: pd.DataFrame, kpi: dict | None) -> None:
        if kpi is None:
            results.to_json(self.export_file_path, index=False)
        else:
            data_structure = {"kpi": kpi, "data": results.to_dict(orient="records")}
            with open(self.export_file_path, "w") as f:
                json.dump(data_structure, f, indent=4)

        export_to_s3 = os.getenv("EXPORT_TO_S3", "False").lower() == "true"
        if export_to_s3:
            timestamp = datetime.now().strftime("%Y_%m_%dT%H_%M_%S")
            base_filename = str(self.export_file_path).split("/")[-1]
            s3_bucket_name = os.getenv("S3_BUCKET_NAME")
            s3_file_key = f"datalake/evaluation_framework/{timestamp}_{base_filename}"
            self.s3_client.upload_file(self.export_file_path, s3_bucket_name, s3_file_key)
            self.logger.info(f"File successfully uploaded {s3_file_key} to S3")

    @abc.abstractmethod
    async def evaluate(self):
        pass

    async def bulk_evaluate(self, max_workers: int = 50) -> list[str]:
        semaphore = asyncio.Semaphore(max_workers)
        results = [None] * len(self.test_cases)
        tasks = []

        async def run_eval(index, test_case):
            async with semaphore:
                result = await self.evaluate(test_case)
                results[index] = result

        for i, test_case in enumerate(self.test_cases):
            task = run_eval(i, test_case)
            tasks.append(task)

        await asyncio.gather(*tasks)
        return results

    def get_metric(self, metric: Metric, **kwargs) -> Assessment:
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": metric.system},
                {"role": "user", "content": metric.prompt.format(**kwargs)},
            ],
            model=metric.model,
        )
        return Assessment.from_string(chat_completion.choices[0].message.content)

    def business_logic(self, conversation: str, business_logic: str, response: str) -> Assessment:
        if business_logic is not None:
            return self.get_metric(
                BUSINESS_LOGIC, conversation=conversation, business_logic=business_logic, response=response
            )
        else:
            return Assessment()

    def faithfullness(self, context: str, response: str) -> Assessment:
        return self.get_metric(FAITHFULLNESS, context=context, response=response)

    def relevance(self, context: str, response: str) -> Assessment:
        return self.get_metric(RELEVANCE, context=context, response=response)

    def rai(self, response: str) -> Assessment:
        return self.get_metric(RAI, response=response)
