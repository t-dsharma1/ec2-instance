from connectai.handlers.utils.calculator.calculator_NBO import calculator_NBO
from connectai.handlers.utils.calculator.calculator_upsell import calculate_upsell

UPSELL_7DAY = "upsell_7day"
UPSELL_30DAY = "upsell_30day"
UPSELL_NBO_1 = "upsell_next_best_offer"
UPSELL_NBO_2 = "upsell-next-best-offer"


def placeholder_calculator(customer_data, flow_type) -> dict:
    """Placeholder function for calculations based on customer data."""
    # Todo: Implement in a elegant way, part of the 'calculator' backlog story.
    if flow_type in [UPSELL_7DAY, UPSELL_30DAY]:
        customer_data = calculate_upsell(customer_data)

    if UPSELL_NBO_1 in flow_type or UPSELL_NBO_2 in flow_type:
        customer_data = calculator_NBO(customer_data)

    return customer_data
