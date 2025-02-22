import pandas as pd
import pytest

from connectai.handlers.utils.calculator.calculator_NBO import (
    NBO_OFFER_APP,
    NBO_OFFER_OPEN,
    NBO_OFFER_VALIDITY,
    calculator_NBO,
)
from connectai.handlers.utils.calculator.NBO_plans import NBO_PLANS

sample_data_maria = {"customer_segment": "maria"}
sample_data_jose = {"customer_segment": "jose"}
sample_data_ana = {"customer_segment": "ana"}
sample_data_juan = {"customer_segment": "juan"}
sample_data_liza = {"customer_segment": "liza"}
sample_data_santos = {"customer_segment": "santos"}
sample_data_grace = {"customer_segment": "grace"}
sample_data_angelica = {"customer_segment": "angelica"}
sample_data_fernando = {"customer_segment": "fernando"}
sample_data_invalid = {"customer_segment": "InvalidSegment"}

nbo_plans_df = pd.DataFrame(NBO_PLANS)


@pytest.mark.parametrize(
    "customer_data, expected_segment",
    [
        (sample_data_maria, "maria"),
        (sample_data_jose, "jose"),
        (sample_data_ana, "ana"),
        (sample_data_juan, "juan"),
        (sample_data_liza, "liza"),
        (sample_data_santos, "santos"),
        (sample_data_grace, "grace"),
        (sample_data_angelica, "angelica"),
        (sample_data_fernando, "fernando"),
    ],
)
def test_calculator_nbo_segments(customer_data, expected_segment):
    result = calculator_NBO(customer_data)
    assert result["customer_segment"] == expected_segment
    assert result["cust_segment"] in ["IncrApp", "IncrOpen", "IncrValidity", "LowData"]


def test_calculator_nbo_price_message():
    sample_data = {"customer_segment": "jose"}
    result = calculator_NBO(sample_data)
    assert result["diff_price"] == result["top1_price"] - result["last_pack_price"]
    assert result["price_message"] == f"for only {result['diff_price']} more than your last pack"


def test_calculator_nbo_no_last_promo():
    sample_data = {"customer_segment": "maria"}
    result = calculator_NBO(sample_data)
    assert result["price_message"] == "for a great price"
    assert result["last_pack_message"] == "The user can find their latest data pack in the Smart app."


@pytest.mark.parametrize(
    "customer_data, expected_message",
    [
        (sample_data_maria, NBO_OFFER_APP),
        (sample_data_jose, NBO_OFFER_OPEN),
        (sample_data_ana, NBO_OFFER_VALIDITY),
    ],
)
def test_calculator_nbo_opening_message_template(customer_data, expected_message):
    result = calculator_NBO(customer_data)
    assert result["opening_message"].startswith(expected_message.split("{recommended_plan}")[0])


def test_calculator_nbo_top5_fields():
    sample_data = {"customer_segment": "angelica"}
    result = calculator_NBO(sample_data)
    assert "top5_price" in result
    assert result["top5_price"] == nbo_plans_df.loc[nbo_plans_df["Promo"] == result["top5_dpd_lm"], "Srp"].values[0]
    assert "top5_total_data" in result
    assert (
        result["top5_total_data"]
        == nbo_plans_df.loc[nbo_plans_df["Promo"] == result["top5_dpd_lm"], "Total Data"].values[0]
    )
