import pytest

from connectai.handlers.utils.calculator_utils import placeholder_calculator
from genie_dao.datamodel._customers import CustomerInformation


class TestCustomer:
    UPSELL_7DAY = "upsell_7day"
    UPSELL_30DAY = "upsell_30day"
    UPSELL_NBO = "upsell_next_best_offer"

    @pytest.mark.parametrize(
        "customer_data, flow_type, expected",
        [
            # Test case for default values
            (
                {
                    "last_pack_price": None,
                    "last_pack_gb": None,
                    "last_pack_min": None,
                    "last_pack_validity": None,
                    "customer_segment": None,
                    "targeted_30day_pack": None,
                    "avg_gb_m1": 0,
                    "avg_gb_m2": 0,
                    "avg_gb_m3": 0,
                    "no_of_month": 10,
                    "pack_purchase_revenue_m1": 0,
                    "pack_purchase_revenue_m2": 0,
                    "pack_purchase_revenue_m3": 0,
                    "remaining_gb": 0,
                    "expiry_in_next_3_days": 0,
                },
                UPSELL_7DAY,
                {
                    "last_pack_price": 0,
                    "last_pack_gb": 0,
                    "last_pack_min": 0,
                    "last_pack_validity": 0,
                    "customer_segment": "199",
                    "targeted_30day_pack": 499,
                },
            ),
            # Test case for filled values
            (
                {
                    "last_pack_price": 100,
                    "last_pack_gb": 10,
                    "last_pack_min": 10,
                    "last_pack_validity": 10,
                    "customer_segment": "798",
                    "targeted_30day_pack": None,
                    "avg_gb_m1": 0,
                    "avg_gb_m2": 0,
                    "avg_gb_m3": 0,
                    "no_of_month": 10,
                    "pack_purchase_revenue_m1": 0,
                    "pack_purchase_revenue_m2": 0,
                    "pack_purchase_revenue_m3": 0,
                    "remaining_gb": 0,
                    "expiry_in_next_3_days": 0,
                },
                UPSELL_7DAY,
                {"last_pack_price": 100, "last_pack_gb": 10, "last_pack_min": 10, "last_pack_validity": 10},
            ),
        ],
    )
    def test_placeholder_calculator(self, customer_data, flow_type, expected):
        """Test the placeholder_calculator function."""
        customer_data = CustomerInformation.from_dict(customer_data)
        # Call the function with the provided calculator data and flow type
        result = placeholder_calculator(customer_data.to_dict(), flow_type)
        # Assert that the result matches the expected data
        for key, value in expected.items():
            assert result[key] == value, f"Error in {key}: expected {value}, got {result[key]}"
