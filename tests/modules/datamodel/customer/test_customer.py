import pytest

from genie_dao.datamodel._customers import CustomerInformation


class TestCustomerInfoGP:
    """Test the JSON loader for the CustomerInfoGP class."""

    @pytest.mark.parametrize(
        "input_data,expected_attributes",
        [
            (
                # Test case 1: Basic attributes
                {
                    "elements": [
                        {
                            "parameter_group": "average_data_volume",
                            "parameter_data": [
                                {"parameter_name": "avg_gb_m1", "parameter_value": "5.00"},
                                {"parameter_name": "avg_gb_m2", "parameter_value": "6.00"},
                                {"parameter_name": "avg_gb_m3", "parameter_value": "4.00"},
                            ],
                        }
                    ]
                },
                {
                    "avg_gb_m1": 5.0,
                    "avg_gb_m2": 6.0,
                    "avg_gb_m3": 4.0,
                },
            ),
            (
                # Test case 2: Comprehensive attributes including missing values
                {
                    "elements": [
                        {
                            "parameter_group": "last_pack",
                            "parameter_data": [
                                {"parameter_name": "last_pack_gb", "parameter_value": "7.00"},
                                {"parameter_name": "last_pack_price", "parameter_value": "200.00"},
                                {"parameter_name": "last_pack_validity", "parameter_value": "7.00"},
                            ],
                        }
                    ]
                },
                {
                    "last_pack_gb": 7.0,
                    "last_pack_min": None,
                    "last_pack_price": 200.0,
                    "last_pack_validity": 7.0,
                },
            ),
        ],
    )
    def test_load(self, input_data, expected_attributes):
        """Test the loading function to ensure it properly parses and sets
        attributes."""
        # Since the class method `load` expects the dictionary after 'customer_context',
        # we simulate this by calling the class method directly with our test data.
        customer_info = CustomerInformation.load({"elements": input_data["elements"]})

        # Check each expected attribute to ensure it matches the customer_info object's attributes
        for attr, expected_value in expected_attributes.items():
            assert getattr(customer_info, attr) == expected_value, f"Mismatch in {attr}"
