HIGH_DATA_PROPOSAL = """ I’m reaching out because I noticed you bought a 7 day data pack this year. \n\nBased on your usage, I wanted to suggest trying our latest 30 day data offer as it may save you some money. If you buy via myGP, you can get {recommended_plan_GB} GB and free OTT access for {recommended_plan_cashback} TK less, at only {price_after_cashback} TK. \n\nIf you want, [here's]({upgrade_link}) the link to buy. What do you think?"""
LOW_DATA_PROPOSAL = """ I’m reaching out because I noticed you bought a 7 day data pack this year. \n\nBased on your usage, I wanted to suggest trying our latest 30 day data offer as it may save you some money. If you buy via myGP, you can get {recommended_plan_GB} GB and free OTT access for {recommended_plan_cashback} TK less, at only {price_after_cashback} TK. \n\nIf you want, [here's]({upgrade_link}) the link to buy. What do you think?"""

OPENING_7DAY_NORMAL = """Hi! I'm AI Bot (Beta), here to help you find the best internet offer for you.\n\nBased on your usage, I recommend our {recommended_plan_GB} GB 30-day data pack for {recommended_plan_price} TK. It's a great balance of volume and price, with longer validity so you won't forget to recharge or accidentally lose unused data. To buy, click [here]({upgrade_link}).\n\nOr chat with me if you want to discuss other data packs. Reply in English or Bangla."""
OPENING_7DAY_AFTER_USER_INTEREST = """Great! I'm here to explain our latest offer: upsized CASHBACK on 30 day data packs if you buy via myGP!\n\nBased on your usage, I recommend our 30 day {recommended_plan_GB} GB pack, now ONLY {recommended_plan_price_after_cashback} TK (usual price {recommended_plan_price} TK!). To buy, click [here]({upgrade_link}). Tell me if you need help."""

OPENING_7DAY_NORMAL_BANGLA = """Hi! I'm AI Bot (Beta). \n\nWe have a limited time cashback offer on our 30 day data packs, saving you up to 220 TK! \n\nInterested to know more? You can reply in English or Bangla."""

OPENING_7DAY_30DAYPACK = (
    """We hope you are happy with your 30-day pack. If you have any questions about it, we are happy to help."""
)

available_packs = {
    "199": {
        "price": 199,
        "gb": 5,
        "ott": "",
        "cashback": 0,
        "url": "https://mygp.grameenphone.com/mygp/recharge?amount=199&channel=recharge_and_activate_trigger&source=MEVRIC",
    },
    "298": {
        "price": 298,
        "gb": 10,
        "ott": "",
        "cashback": 0,
        "url": "https://mygp.grameenphone.com/mygp/recharge?amount=298&channel=recharge_and_activate_trigger&source=MEVRIC",
    },
    "399": {
        "price": 399,
        "gb": 12,
        "ott": "",
        "cashback": 0,
        "url": "https://mygp.grameenphone.com/mygp/recharge?amount=399&channel=recharge_and_activate_trigger&source=MEVRIC",
    },
    "499": {
        "price": 499,
        "gb": 25,
        "ott": "",
        "cashback": 20,
        "url": "https://mygp.grameenphone.com/mygp/recharge?amount=499&channel=recharge_and_activate_trigger&source=MEVRIC",
    },
    "599": {
        "price": 599,
        "gb": 40,
        "ott": "",
        "cashback": 0,
        "url": "https://mygp.grameenphone.com/mygp/recharge?amount=599&channel=recharge_and_activate_trigger&source=MEVRIC",
    },
    "699": {
        "price": 699,
        "gb": 60,
        "ott": "HOICHOI, CHORKI and T-SPORTS",
        "cashback": 80,
        "url": "https://mygp.grameenphone.com/mygp/recharge?amount=699&channel=recharge_and_activate_trigger&source=MEVRIC",
    },
    "798": {
        "price": 798,
        "gb": 100,
        "ott": "HOICHOI, CHORKI, T-SPORTS and SONYLIV",
        "cashback": 120,
        "url": "https://mygp.grameenphone.com/mygp/recharge?amount=798&channel=recharge_and_activate_trigger&source=MEVRIC",
    },
}


def calculate_upsell(cust_data) -> dict:
    # Default values for last pack
    if not cust_data["last_pack_price"] or type(cust_data["last_pack_price"]) == str:
        cust_data["last_pack_price"] = 0
    if not cust_data["last_pack_gb"] or type(cust_data["last_pack_gb"]) == str:
        cust_data["last_pack_gb"] = 0
    if not cust_data["last_pack_min"] or type(cust_data["last_pack_min"]) == str:
        cust_data["last_pack_min"] = 0
    if not cust_data["last_pack_validity"] or type(cust_data["last_pack_validity"]) == str:
        cust_data["last_pack_validity"] = 0
    if not cust_data["customer_segment"] or type(cust_data["customer_segment"]) == float:
        cust_data["customer_segment"] = list(available_packs.keys())[0]
    if not cust_data["targeted_30day_pack"] or type(cust_data["targeted_30day_pack"]) == str:
        cust_data["targeted_30day_pack"] = 499
    if not cust_data["remaining_gb"] or type(cust_data["remaining_gb"]) == str:
        cust_data["remaining_gb"] = 2.22
    if not cust_data["expiry_in_next_3_days"] or type(cust_data["expiry_in_next_3_days"]) == str:
        cust_data["expiry_in_next_3_days"] = 1.11

    # Other fields that might be empty or datatype is string
    if not cust_data["avg_gb_m1"] or type(cust_data["avg_gb_m1"]) == str:
        cust_data["avg_gb_m1"] = 0
    if not cust_data["avg_gb_m2"] or type(cust_data["avg_gb_m2"]) == str:
        cust_data["avg_gb_m2"] = 0
    if not cust_data["avg_gb_m3"] or type(cust_data["avg_gb_m3"]) == str:
        cust_data["avg_gb_m3"] = 0
    if not cust_data["pack_purchase_revenue_m1"] or type(cust_data["pack_purchase_revenue_m1"]) == str:
        cust_data["pack_purchase_revenue_m1"] = 0
    if not cust_data["pack_purchase_revenue_m2"] or type(cust_data["pack_purchase_revenue_m2"]) == str:
        cust_data["pack_purchase_revenue_m2"] = 0
    if not cust_data["pack_purchase_revenue_m3"] or type(cust_data["pack_purchase_revenue_m3"]) == str:
        cust_data["pack_purchase_revenue_m3"] = 0
    if not cust_data["no_of_month"] or type(cust_data["no_of_month"]) == str:
        cust_data["no_of_month"] = 0

    # Round values & calculate average usage
    cust_data["pack_purchase_revenue_m1"] = int(cust_data["pack_purchase_revenue_m1"])
    cust_data["avg_gb_m1"] = int(cust_data["avg_gb_m1"] / 1000)
    cust_data["avg_gb_m2"] = int(cust_data["avg_gb_m2"] / 1000)
    cust_data["avg_gb_m3"] = int(cust_data["avg_gb_m3"] / 1000)
    cust_data["last_pack_price"] = int(cust_data["last_pack_price"])
    cust_data["no_of_month"] = int(cust_data["no_of_month"])
    cust_data["last_pack_min"] = int(cust_data["last_pack_min"])
    cust_data["last_pack_validity"] = int(cust_data["last_pack_validity"])

    cust_data["remaining_gb"] = round(cust_data["remaining_gb"], 1)
    cust_data["expiry_in_next_3_days"] = round(cust_data["expiry_in_next_3_days"], 1)
    cust_data["last_pack_gb"] = round(cust_data["last_pack_gb"], 1)

    cust_data["GB_average"] = round((cust_data["avg_gb_m1"] + cust_data["avg_gb_m2"] + cust_data["avg_gb_m3"]) / 3, 1)

    cust_data["purchase_average"] = int(
        (
            cust_data["pack_purchase_revenue_m1"]
            + cust_data["pack_purchase_revenue_m2"]
            + cust_data["pack_purchase_revenue_m3"]
        )
        / 3
    )

    cust_data["recommended_plan"] = (
        cust_data["customer_segment"]
        if cust_data["customer_segment"] in available_packs.keys()
        else list(available_packs.keys())[0]
    )

    cust_data["recommended_plan_GB"] = (
        available_packs[cust_data["customer_segment"]]["gb"]
        if cust_data["customer_segment"] in available_packs.keys()
        else list(available_packs.values())[0]["gb"]
    )

    cust_data["recommended_plan_price"] = (
        available_packs[cust_data["customer_segment"]]["price"]
        if cust_data["customer_segment"] in available_packs.keys()
        else list(available_packs.values())[0]["price"]
    )

    cust_data["recommended_plan_OTT"] = (
        available_packs[cust_data["customer_segment"]]["ott"]
        if cust_data["customer_segment"] in available_packs.keys()
        else list(available_packs.values())[0]["ott"]
    )

    cust_data["recommended_plan_cashback"] = (
        available_packs[cust_data["customer_segment"]]["cashback"]
        if cust_data["customer_segment"] in available_packs.keys()
        else list(available_packs.values())[0]["cashback"]
    )

    cust_data["price_after_cashback"] = cust_data["recommended_plan_price"] - cust_data["recommended_plan_cashback"]

    # Calculations for price per GB. The latest pack will not always be provided for UC1
    cust_data["last_pack_price_per_GB"] = (
        cust_data["last_pack_price"] / cust_data["last_pack_gb"] if cust_data["last_pack_gb"] > 0 else 0
    )

    # Sentence describing latest pack, depending on if its provided
    cust_data["last_pack_info"] = (
        f"is a {cust_data['last_pack_validity']} day pack with {cust_data['last_pack_gb']} GB data for a price of {cust_data['last_pack_price']} TK"
        if cust_data["last_pack_validity"] > 0 and cust_data["last_pack_gb"] > 0
        else "can be found in the myGP app"
    )

    cust_data["upgrade_link"] = (
        available_packs[cust_data["customer_segment"]]["url"]
        if cust_data["customer_segment"] in available_packs.keys()
        else list(available_packs.values())[0]["url"]
    )

    cust_data["renewal_link"] = "https://mygp.grameenphone.com/mygp/balance/internet?source=MEVRIC"

    cust_data["7day_first_message"] = (
        OPENING_7DAY_NORMAL.format(
            recommended_plan_price=cust_data["recommended_plan_price"],
            recommended_plan_GB=cust_data["recommended_plan_GB"],
            upgrade_link=cust_data["upgrade_link"],
        )
        if cust_data["last_pack_validity"] != 30
        else OPENING_7DAY_30DAYPACK
    )
    cust_data["7day_first_message_bangla"] = (
        OPENING_7DAY_NORMAL_BANGLA if cust_data["last_pack_validity"] != 30 else OPENING_7DAY_30DAYPACK
    )
    cust_data["7day_message_after_user_interest"] = (
        OPENING_7DAY_AFTER_USER_INTEREST.format(
            recommended_plan_price=cust_data["recommended_plan_price"],
            recommended_plan_price_after_cashback=cust_data["price_after_cashback"],
            recommended_plan_GB=cust_data["recommended_plan_GB"],
            upgrade_link=cust_data["upgrade_link"],
        )
        if cust_data["last_pack_validity"] != 30
        else OPENING_7DAY_30DAYPACK
    )

    cust_data["proposal_message"] = (
        HIGH_DATA_PROPOSAL if cust_data["avg_gb_m1"] > 0.5 * cust_data["recommended_plan_GB"] else LOW_DATA_PROPOSAL
    )

    # Parsing of opening message
    cust_data["proposal_message"] = cust_data["proposal_message"].format(
        recommended_plan_GB=cust_data["recommended_plan_GB"],
        recommended_plan_cashback=cust_data["recommended_plan_cashback"],
        price_after_cashback=cust_data["price_after_cashback"],
        upgrade_link=cust_data["upgrade_link"],
    )
    return cust_data
