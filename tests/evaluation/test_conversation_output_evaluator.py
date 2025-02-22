import json
import os
import pathlib
from datetime import datetime
from unittest import mock
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

from connectai.evaluation.conversation_output_agent.evaluator import (
    EvaluateConversationOutputAgent,
)

test_cases_json = json.dumps(
    [
        {
            "conversation_id": "003",
            "checkpoint": 2,
            "user_input": "data_habits",
            "from_state_name": "ANY",
            "ground_truth_state_name": "CONTINUE_ENRICHING_CONVERSION_DATA",
            "business_logic": "The assistant asks about the number of SIM, lines or connections that the user needs.",
        },
        {
            "flow": "lead_acquisition",
            "user_input": "mobility_product",
            "from_state_name": "ANY",
            "ground_truth_state_name": "MOBILITY_INFORMATION",
        }
        # Add more test cases as needed
    ]
)


@pytest.fixture
def base_evaluator():
    with mock.patch("connectai.handlers.get_or_create_logger", return_value=MagicMock()):
        with mock.patch(
            "connectai.evaluation.evaluator.BaseEvaluator.get_test_case_path", return_value="test_case_path.json"
        ):
            with mock.patch("builtins.open", mock.mock_open(read_data=test_cases_json)):
                with mock.patch("connectai.evaluation.factory.test_factory.TestFactory.fetch_flows", return_value={}):
                    with mock.patch(
                        "connectai.evaluation.factory.test_factory.TestFactory.fetch_user_messages",
                        return_value={"data_habits": ["message1"], "mobility_product": ["message2"]},
                    ):
                        with mock.patch(
                            "connectai.evaluation.factory.test_factory.TestFactory.fetch_conversation",
                            return_value=(MagicMock(), MagicMock(), "flow_type"),
                        ):
                            with mock.patch(
                                "connectai.evaluation.factory.test_factory.TestFactory.fetch_context",
                                return_value="context",
                            ):
                                with mock.patch("boto3.client"):
                                    evaluator = EvaluateConversationOutputAgent(export_filename="test_export.json")
                                    evaluator.s3_client = MagicMock()
                                    evaluator.test_cases = [{"test_case": 1}, {"test_case": 2}]  # Example test cases
                                    yield evaluator


def test_create_export_path(base_evaluator):
    expected_path = pathlib.Path("src/connectai/evaluation/results/test_export.json")
    path = base_evaluator._create_export_path("test_export.json")
    assert path == expected_path


def test_build_test_cases(base_evaluator):
    with mock.patch("builtins.open", mock.mock_open(read_data=test_cases_json)):
        cases = base_evaluator._build_test_cases("test_case_path.json")
    assert len(cases) == 2  # Assuming build method transforms each dict into one case


def test_format_conversation(base_evaluator):
    conversation_history = MagicMock()
    conversation_history.as_prompt_messages.return_value = [
        MagicMock(role="user", content="Hello"),
        MagicMock(role="assistant", content="Hi there!"),
    ]
    formatted = base_evaluator.format_conversation(conversation_history)
    assert formatted == "USER: Hello\n----\nASSISTANT: Hi there!"


def test_export_to_json(base_evaluator):
    results = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    with patch("builtins.open", mock.mock_open()) as mock_file:
        base_evaluator.export(results, None)
        mock_file().write.assert_called_once()


def test_export_with_kpi(base_evaluator):
    results = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    kpi = {"metric1": 0.9}
    with patch("builtins.open", mock.mock_open()) as mock_file:
        base_evaluator.export(results, kpi)
        mock_file().write.assert_called()


def test_export_to_s3(base_evaluator):
    os.environ["EXPORT_TO_S3"] = "true"
    os.environ["S3_BUCKET_NAME"] = "test_bucket"
    base_evaluator.export_file_path = "test_export.json"
    base_evaluator.logger = MagicMock()

    with mock.patch("connectai.evaluation.evaluator.base_evaluator.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 1, 1)
        base_evaluator.export(pd.DataFrame(), None)

    base_evaluator.s3_client.upload_file.assert_called_once_with(
        "test_export.json", "test_bucket", "datalake/evaluation_framework/2023_01_01T00_00_00_test_export.json"
    )
    base_evaluator.logger.info.assert_called_once()


def test_get_metric(base_evaluator):
    with mock.patch.object(
        base_evaluator.client.chat.completions,
        "create",
        return_value=MagicMock(choices=[MagicMock(message=MagicMock(content="result"))]),
    ):
        metric = MagicMock(system="system", prompt="prompt {param}", model="model")
        result = base_evaluator.get_metric(metric, param="value")
        assert result.assessment == ""


@pytest.mark.asyncio
async def test_bulk_evaluate(base_evaluator):
    async def mock_evaluate(test_case):
        return {"test_case": f"result_{test_case['test_case']}"}

    base_evaluator.evaluate = mock_evaluate

    results = await base_evaluator.bulk_evaluate()
    assert results == [{"test_case": "result_1"}, {"test_case": "result_2"}]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_evaluate(base_evaluator):
    test_case = MagicMock()
    test_case.ground_truth_state_name = "TEST_STATE"
    mock_conversation_history = MagicMock()
    mock_conversation_history.append_to_history.return_value = mock_conversation_history
    mock_conversation_history.as_prompt_messages.return_value = [
        MagicMock(role="user", content="Hello"),
        MagicMock(role="assistant", content="Hi there!"),
    ]
    test_case.conversation_history = mock_conversation_history
    test_case.user_input.content = "user input"

    flow_factory = MagicMock()
    flow = AsyncMock()
    flow.run_test.return_value = MagicMock(llm_response="response")
    flow.flow_config._flow_config = {"verbosity": 50}
    with mock.patch(
        "connectai.modules.state_machine.loaders.flow_factory.FlowFactory.create_flow_from_local", return_value=flow
    ):
        result = await base_evaluator.evaluate(test_case)

    assert result["Response"] == "response"


def test_format_results(base_evaluator):
    test_case = MagicMock()
    test_case.name = "001"
    test_case.conversation_history = MagicMock()
    test_case.user_input.content = "user input"
    test_case.from_state_name = "FROM_STATE"
    test_case.ground_truth_state_name = "GROUND_TRUTH_STATE"
    test_case.business_logic = "business logic"
    test_case.context = "context"
    test_case.customer_features.to_json.return_value = '{"feature": "value"}'

    business_logic = MagicMock(assessment="Yes", reasoning="Business Logic Reasoning")
    faithfullness = MagicMock(assessment="Yes", reasoning="Faithfullness Reasoning")
    relevance = MagicMock(assessment="Yes", reasoning="Relevance Reasoning")
    rai = MagicMock(assessment="Yes", reasoning="RAI Reasoning")
    llama_guard = "Yes"
    verbosity_results = {"word_count": 10, "verbosity": 5}

    result = base_evaluator.format_results(
        test_case, "response", business_logic, faithfullness, relevance, rai, llama_guard, verbosity_results
    )

    assert result["Test Id"] == "001"
    assert result["Response"] == "response"
    assert result["Business Logic Eval"] == "Yes"


def test_calculate_kpi(base_evaluator):
    results_table = pd.DataFrame(
        {
            "Business Logic Eval": ["Yes", "No"],
            "Faithfullness Eval": ["Yes", "Yes"],
            "Relevance Eval": ["Yes", "No"],
            "RAI Eval": ["Yes", "No"],
            "Llama Guard Eval": ["Yes", "Yes"],
            "Business Logic": ["business logic", None],  # Add this line to ensure the key exists
            "Is Exceed": [10, 0],
            "Word Exceed Count": [5, 0],
        }
    )

    kpi = base_evaluator.calculate_kpi(results_table)

    assert kpi["coupled"]["average"]["Business Logic Eval"] == 1.0
    assert kpi["decoupled"]["average"]["Faithfullness Eval"] == 1.0
