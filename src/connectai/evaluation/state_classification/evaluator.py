import asyncio

import pandas as pd

from connectai.evaluation.evaluator import BaseEvaluator
from connectai.evaluation.factory import TestCase
from connectai.handlers.utils.calculator_utils import placeholder_calculator
from connectai.modules.datamodel import RuntimeContext
from connectai.modules.state_machine.loaders.flow_factory import FlowFactory


class EvaluateState(BaseEvaluator):
    """Evaluate the state classification."""

    async def evaluate(self, test: TestCase) -> str:
        flow_factory = FlowFactory(flow_type=test.flow)
        flow = flow_factory.create_flow_from_local()

        try:
            customer_data = placeholder_calculator({}, test.flow)
        except TypeError:
            customer_data = {}
        except KeyError:
            customer_data = {}

        try:
            response = await flow.run_test(
                start_state_name=test.from_state_name,
                runtime_context=RuntimeContext(
                    conversation=test.conversation_history.append_to_history(test.user_input),
                    extra_info={**customer_data},
                ),
            )
            return response
        except:
            return "HALLUCINATION"

    async def evaluate_all(self, max_workers: int = 35) -> pd.DataFrame:
        results = await self.bulk_evaluate(max_workers=max_workers)
        return self.format_results_table(results)

    def format_results_table(self, results: list[str]) -> pd.DataFrame:
        formatted_results = []
        for test, result in zip(self.test_cases, results):
            res = {}
            res["Test Id"] = str(test.name)
            res["Conversation"] = self.format_conversation(test.conversation_history)
            res["User Input"] = test.user_input.content
            res["Dialogue Flow"] = test.flow
            res["From State"] = test.from_state_name
            res["Ground Truth State"] = test.ground_truth_state_name
            res["Business Logic"] = test.business_logic
            res["Context"] = test.context
            res["Customer Features"] = test.customer_features.to_json()
            res["Results"] = result
            res["Evaluation"] = 1 if result == test.ground_truth_state_name else 0
            formatted_results.append(res)
        return pd.DataFrame(formatted_results)

    def calculate_kpi(self, results_table: pd.DataFrame) -> dict[str, str]:
        return {
            "average": results_table["Evaluation"].mean().round(2),
            "min": results_table.groupby(["From State", "Ground Truth State"])["Evaluation"].mean().round(2).min(),
            "no_test_cases": results_table.shape[0],
        }


async def main():
    evaluator = EvaluateState(export_filename="state_classification.json")
    results = await evaluator.evaluate_all()
    kpi = evaluator.calculate_kpi(results)
    evaluator.export(results, kpi)


if __name__ == "__main__":
    asyncio.run(main())
