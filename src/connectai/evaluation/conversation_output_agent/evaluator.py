import asyncio
import re

import pandas as pd

from connectai.evaluation.evaluator import BaseEvaluator, LlamaGuard
from connectai.evaluation.factory import TestCase
from connectai.handlers.utils.calculator_utils import placeholder_calculator
from connectai.modules.datamodel import RuntimeContext
from connectai.modules.state_machine.loaders.flow_factory import FlowFactory


class EvaluateConversationOutputAgent(BaseEvaluator):
    """Evaluate the conversation output agent."""

    llama_guard = LlamaGuard()

    async def evaluate(self, test: TestCase) -> dict[str, str]:
        flow_factory = FlowFactory(flow_type=test.flow)
        flow = flow_factory.create_flow_from_local()

        try:
            customer_data = placeholder_calculator({}, test.flow)
        except TypeError:
            customer_data = {}

        response = await flow.run_test(
            start_state_name=test.ground_truth_state_name,
            runtime_context=RuntimeContext(
                conversation=test.conversation_history.append_to_history(test.user_input), extra_info={**customer_data}
            ),
            compute_llm_response=True,
        )
        res = response.llm_response
        business_logic = self.business_logic(
            conversation=self.format_conversation(test.conversation_history.append_to_history(test.user_input)),
            business_logic=test.business_logic,
            response=res,
        )
        faithfullness = self.faithfullness(context=test.context, response=res)
        # llama_guard = self.llama_guard.run_output(res)
        llama_guard = "NOT AVAILABLE"  # FIXME: Llama-Guard is not supported in AnyScale any longer.
        rai = self.rai(response=res)
        relevance = self.relevance(context=test.context, response=res)

        # Verbosity evaluation
        verbosity = flow.flow_config._flow_config["verbosity"]
        word_count = self._get_word_count(res)
        verbosity_results = {"verbosity": verbosity, "word_count": word_count}

        return self.format_results(
            test, res, business_logic, faithfullness, relevance, rai, llama_guard, verbosity_results
        )

    @staticmethod
    def _get_word_count(sentence: str) -> int:
        # Only retain words and whitespace (strips emoji, punctuation, etc.)
        return len(re.sub(r"[^\w\s]", "", sentence).split())

    async def evaluate_all(self, max_workers: int = 10) -> pd.DataFrame:
        results = await self.bulk_evaluate(max_workers=max_workers)
        return pd.DataFrame(results)

    def format_results(
        self, test_case, response, business_logic, faithfullness, relevance, rai, llama_guard, verbosity_results
    ) -> dict[str, str]:
        res = {}
        res["Test Id"] = str(test_case.name)
        res["Conversation"] = self.format_conversation(test_case.conversation_history)
        res["User Input"] = test_case.user_input.content
        res["From State"] = test_case.from_state_name
        res["Ground Truth State"] = test_case.ground_truth_state_name
        res["Business Logic"] = test_case.business_logic
        res["Context"] = test_case.context
        res["Customer Features"] = test_case.customer_features.to_json()
        res["Response"] = response
        res["Business Logic Eval"] = business_logic.assessment
        res["Business Logic Reasoning"] = business_logic.reasoning
        res["Faithfullness Eval"] = faithfullness.assessment
        res["Faithfullness Reasoning"] = faithfullness.reasoning
        res["Relevance Eval"] = relevance.assessment
        res["Relevance Reasoning"] = relevance.reasoning
        res["RAI Eval"] = rai.assessment
        res["RAI Reasoning"] = rai.reasoning
        res["Llama Guard Eval"] = llama_guard  # .assessment
        res["Is Exceed"] = verbosity_results["word_count"] > verbosity_results["verbosity"]
        res["Word Exceed Count"] = max(verbosity_results["word_count"] - verbosity_results["verbosity"], 0)
        return res

    def calculate_kpi(self, results_table: pd.DataFrame):
        results_table["RAI Eval"] = results_table["RAI Eval"].str.replace("No", "Yes")
        results_table["Llama Guard Eval"] = results_table["Llama Guard Eval"].str.replace("safe", "Yes")

        coupled = results_table.dropna(subset=["Business Logic"]).copy()
        decoupled = results_table[results_table["Business Logic"].isna()].copy()

        coupled_accuracy = (
            (
                coupled[["Business Logic Eval", "Faithfullness Eval", "Relevance Eval", "RAI Eval", "Llama Guard Eval"]]
                == "Yes"
            )
            .mean()
            .round(2)
        )
        decoupled_accuracy = (
            (decoupled[["Faithfullness Eval", "Relevance Eval", "RAI Eval", "Llama Guard Eval"]] == "Yes")
            .mean()
            .round(2)
        )
        verbosity = {
            "no_test_cases": len(results_table),
            "no_exceed_verbosity_cases": int(results_table["Is Exceed"].sum()),
            "verbosity_exceed_count_50_pct": int(results_table["Word Exceed Count"].quantile(0.5)),
            "verbosity_exceed_count_90_pct": int(results_table["Word Exceed Count"].quantile(0.9)),
            "verbosity_exceed_count_99_pct": int(results_table["Word Exceed Count"].quantile(0.99)),
        }

        return {
            "coupled": {"average": coupled_accuracy.to_dict(), "no_test_cases": coupled.shape[0]},
            "decoupled": {"average": decoupled_accuracy.to_dict(), "no_test_cases": decoupled.shape[0]},
            "verbosity": verbosity,
        }


async def main():
    evaluator = EvaluateConversationOutputAgent(export_filename="conversation_output_agent.json")
    results = await evaluator.evaluate_all()
    kpi = evaluator.calculate_kpi(results)
    evaluator.export(results, kpi)


if __name__ == "__main__":
    asyncio.run(main())
