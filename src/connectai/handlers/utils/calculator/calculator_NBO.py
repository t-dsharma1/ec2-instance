import pandas as pd

from connectai.handlers.utils.calculator.NBO_plans import NBO_PLANS

NBO_OFFER_APP = """Hi, I'm AI Bot (Beta), here to recommend a prepaid offer based on your needs. \n\n Stream and scroll endlessly with {recommended_plan}. Get <PRODUCT INFO> {price_message}! \n\nClick [here]({upgrade_link}) to avail, or share any questions or doubts below."""
NBO_OFFER_OPEN = """Hi, I'm AI Bot (Beta), here to recommend a prepaid offer based on your needs. \n\nUse your data with more flexibility with {recommended_plan}. Get <PRODUCT INFO> {price_message}! \n\nClick [here]({upgrade_link}) to avail, or share any questions or doubts below."""
NBO_OFFER_VALIDITY = """Hi, I'm AI Bot (Beta), here to recommend a prepaid offer based on your needs. \n\nLonger validity, less hassle with {recommended_plan}. Get <PRODUCT INFO> {price_message}! \n\nClick [here]({upgrade_link}) to avail, or share any questions or doubts below."""
NBO_OFFER_OTHER = """Hi, I'm AI Bot (Beta), here to recommend a prepaid offer based on your needs. \n\nJust enough data, with great value: {recommended_plan}. Get <PRODUCT INFO> {price_message}! \n\nClick [here]({upgrade_link}) to avail, or share any questions or doubts below."""


def calculator_NBO(cust_data) -> dict:
    nbo_plans = pd.DataFrame(NBO_PLANS)

    # Revert to default value for customer_segment if not provided
    cust_data["customer_segment"] = "" if "customer_segment" not in cust_data.keys() else cust_data["customer_segment"]
    if cust_data["customer_segment"].lower() not in [
        "maria",
        "jose",
        "ana",
        "juan",
        "liza",
        "santos",
        "grace",
        "ronaldo",
        "angelica",
        "fernando",
    ]:
        cust_data["customer_segment"] = "jose"

    # Parsing of API fields, hardcoded per personality
    if cust_data["customer_segment"].lower() == "maria":
        cust_data["top1_dpd_lm"] = "GIGA VIDEO 50"
        cust_data["top2_dpd_lm"] = "GIGA VIDEO 99"
        cust_data["top3_dpd_lm"] = "CTS 29"
        cust_data["top4_dpd_lm"] = "GIGA STORIES 50"
        cust_data["top5_dpd_lm"] = "ALL DATA 50"
        cust_data["cust_segment"] = "IncrApp"
        cust_data["last_promo"] = None
        cust_data["most_freq_srp"] = None
        cust_data["tot_data_vol_mb_30days"] = 0.02
    elif cust_data["customer_segment"].lower() == "jose":
        cust_data["top1_dpd_lm"] = "ALL DATA 99"
        cust_data["top2_dpd_lm"] = "ALL DATA 299"
        cust_data["top3_dpd_lm"] = "ALL DATA 50"
        cust_data["top4_dpd_lm"] = "POWER ALL 99"
        cust_data["top5_dpd_lm"] = "MAGIC DATA 99"
        cust_data["cust_segment"] = "IncrOpen"
        cust_data["last_promo"] = "ALL DATA 50"
        cust_data["most_freq_srp"] = 50
        cust_data["tot_data_vol_mb_30days"] = 1191.97
    elif cust_data["customer_segment"].lower() == "ana":
        cust_data["top1_dpd_lm"] = "MAGIC DATA 199"
        cust_data["top2_dpd_lm"] = "MAGIC DATA 399"
        cust_data["top3_dpd_lm"] = "MAGIC DATA 99"
        cust_data["top4_dpd_lm"] = "ALL DATA 299"
        cust_data["top5_dpd_lm"] = "GIGA STORIES 299"
        cust_data["cust_segment"] = "IncrValidity"
        cust_data["last_promo"] = "ALL DATA+ 149"
        cust_data["most_freq_srp"] = 149
        cust_data["tot_data_vol_mb_30days"] = 3200.76
    elif cust_data["customer_segment"].lower() == "juan":
        cust_data["top1_dpd_lm"] = "ALLNET 50"
        cust_data["top2_dpd_lm"] = "ALLNET 99"
        cust_data["top3_dpd_lm"] = "ALLNET 30"
        cust_data["top4_dpd_lm"] = "DOUBLE GIGA STORIES+ 65 UACT"
        cust_data["top5_dpd_lm"] = "DOUBLE GIGA VIDEO+ 65 UACT"
        cust_data["cust_segment"] = "IncrOpen"
        cust_data["last_promo"] = "ALLNET 30"
        cust_data["most_freq_srp"] = 30
        cust_data["tot_data_vol_mb_30days"] = 0.00
    elif cust_data["customer_segment"].lower() == "liza":
        cust_data["top1_dpd_lm"] = "DOUBLE GIGA VIDEO+ 65 UACT"
        cust_data["top2_dpd_lm"] = "DOUBLE GIGA VIDEO+ 130 UACT"
        cust_data["top3_dpd_lm"] = "GIGA VIDEO 50"
        cust_data["top4_dpd_lm"] = "DOUBLE GIGA STORIES+ 65 UACT"
        cust_data["top5_dpd_lm"] = "DOUBLE GIGA STORIES+ 130 UACT"
        cust_data["cust_segment"] = "LowData"
        cust_data["last_promo"] = "GIGA VIDEO 99"
        cust_data["most_freq_srp"] = 50
        cust_data["tot_data_vol_mb_30days"] = 1328.22
    elif cust_data["customer_segment"].lower() == "santos":
        cust_data["top1_dpd_lm"] = "ALLNET 30"
        cust_data["top2_dpd_lm"] = "ALLNET 50"
        cust_data["top3_dpd_lm"] = "AOS 20"
        cust_data["top4_dpd_lm"] = "ALLNET 99"
        cust_data["top5_dpd_lm"] = "DOUBLE GIGA STORIES+ 65 UACT"
        cust_data["cust_segment"] = "LowData"
        cust_data["last_promo"] = None
        cust_data["most_freq_srp"] = 111.5
        cust_data["tot_data_vol_mb_30days"] = 3.82
    elif cust_data["customer_segment"].lower() == "grace":
        cust_data["top1_dpd_lm"] = "UNLI DATA 999-60D"
        cust_data["top2_dpd_lm"] = "UNLI DATA 1199-90D"
        cust_data["top3_dpd_lm"] = "UNLI DATA 599-30D"
        cust_data["top4_dpd_lm"] = "DOUBLE GIGA STORIES+ 749"
        cust_data["top5_dpd_lm"] = "DOUBLE GIGA VIDEO+ 749"
        cust_data["cust_segment"] = "IncrValidity"
        cust_data["last_promo"] = "UNLI 5G with Extra 4G 599"
        cust_data["most_freq_srp"] = 599
        cust_data["tot_data_vol_mb_30days"] = 3261.11
    elif cust_data["customer_segment"].lower() == "ronaldo":
        cust_data["top1_dpd_lm"] = "DOUBLE GIGA STORIES+ 399 UACT"
        cust_data["top2_dpd_lm"] = "DOUBLE GIGA STORIES+ 749"
        cust_data["top3_dpd_lm"] = "ALLNET 299"
        cust_data["top4_dpd_lm"] = "DOUBLE GIGA STORIES+ 399 UACT"
        cust_data["top5_dpd_lm"] = "MAGIC DATA 399"
        cust_data["cust_segment"] = "IncrApp"
        cust_data["last_promo"] = "ALLNET 299"
        cust_data["most_freq_srp"] = 299
        cust_data["tot_data_vol_mb_30days"] = 0.0
    elif cust_data["customer_segment"].lower() == "angelica":
        cust_data["top1_dpd_lm"] = "DOUBLE GIGA STORIES+ 65 UACT"
        cust_data["top2_dpd_lm"] = "DOUBLE GIGA STORIES+ 130 UACT"
        cust_data["top3_dpd_lm"] = "ALLNET 50"
        cust_data["top4_dpd_lm"] = "DOUBLE GIGA VIDEO+ 65 UACT"
        cust_data["top5_dpd_lm"] = "GIGA VIDEO 99"
        cust_data["cust_segment"] = "IncrApp"
        cust_data["last_promo"] = "UCT 50"
        cust_data["most_freq_srp"] = 50
        cust_data["tot_data_vol_mb_30days"] = 0.0
    elif cust_data["customer_segment"].lower() == "fernando":
        cust_data["top1_dpd_lm"] = "ALLNET 30"
        cust_data["top2_dpd_lm"] = "ALLNET 50"
        cust_data["top3_dpd_lm"] = "AOS 20"
        cust_data["top4_dpd_lm"] = "CTS 49"
        cust_data["top5_dpd_lm"] = "AOS 50"
        cust_data["cust_segment"] = "IncrOpen"
        cust_data["last_promo"] = "CTC 20"
        cust_data["most_freq_srp"] = 10
        cust_data["tot_data_vol_mb_30days"] = 0.0

    # Preprocessing API input
    cust_data["tot_data_vol_mb_30days"] = round(cust_data["tot_data_vol_mb_30days"] / 1000, 1)

    # Parsing of parameters for top 1 pack
    cust_data["top1_price"] = int(nbo_plans.loc[nbo_plans["Promo"] == cust_data["top1_dpd_lm"], "Srp"].values[0])
    cust_data["top1_validity"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top1_dpd_lm"], "Validity"].values[0]
    cust_data["top1_min"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top1_dpd_lm"], "Voice"].values[0]
    cust_data["top1_sms"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top1_dpd_lm"], "Sms"].values[0]
    cust_data["top1_gb"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top1_dpd_lm"], "Plain Data"].values[0]
    cust_data["top1_app"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top1_dpd_lm"], "Apps"].values[0]
    cust_data["top1_total_app_data"] = nbo_plans.loc[
        nbo_plans["Promo"] == cust_data["top1_dpd_lm"], "Total App Data"
    ].values[0]
    cust_data["top1_total_plain_data"] = nbo_plans.loc[
        nbo_plans["Promo"] == cust_data["top1_dpd_lm"], "Total Plain Data"
    ].values[0]
    cust_data["top1_total_data"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top1_dpd_lm"], "Total Data"].values[0]
    # TODO: replace
    cust_data["top1_link"] = "https://smart.com.ph/prepaid"

    # Parsing of parameters for top 2 pack
    cust_data["top2_price"] = int(nbo_plans.loc[nbo_plans["Promo"] == cust_data["top2_dpd_lm"], "Srp"].values[0])
    cust_data["top2_validity"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top2_dpd_lm"], "Validity"].values[0]
    cust_data["top2_min"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top2_dpd_lm"], "Voice"].values[0]
    cust_data["top2_sms"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top2_dpd_lm"], "Sms"].values[0]
    cust_data["top2_gb"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top2_dpd_lm"], "Plain Data"].values[0]
    cust_data["top2_app"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top2_dpd_lm"], "Apps"].values[0]
    cust_data["top2_total_app_data"] = nbo_plans.loc[
        nbo_plans["Promo"] == cust_data["top2_dpd_lm"], "Total App Data"
    ].values[0]
    cust_data["top2_total_plain_data"] = nbo_plans.loc[
        nbo_plans["Promo"] == cust_data["top2_dpd_lm"], "Total Plain Data"
    ].values[0]
    cust_data["top2_total_data"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top2_dpd_lm"], "Total Data"].values[0]
    # TODO: replace
    cust_data["top2_link"] = "https://smart.com.ph/prepaid"

    # Parsing of parameters for top 3 pack
    cust_data["top3_price"] = int(nbo_plans.loc[nbo_plans["Promo"] == cust_data["top3_dpd_lm"], "Srp"].values[0])
    cust_data["top3_validity"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top3_dpd_lm"], "Validity"].values[0]
    cust_data["top3_min"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top3_dpd_lm"], "Voice"].values[0]
    cust_data["top3_sms"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top3_dpd_lm"], "Sms"].values[0]
    cust_data["top3_gb"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top3_dpd_lm"], "Plain Data"].values[0]
    cust_data["top3_app"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top3_dpd_lm"], "Apps"].values[0]
    cust_data["top3_total_app_data"] = nbo_plans.loc[
        nbo_plans["Promo"] == cust_data["top3_dpd_lm"], "Total App Data"
    ].values[0]
    cust_data["top3_total_plain_data"] = nbo_plans.loc[
        nbo_plans["Promo"] == cust_data["top3_dpd_lm"], "Total Plain Data"
    ].values[0]
    cust_data["top3_total_data"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top3_dpd_lm"], "Total Data"].values[0]
    # TODO: replace
    cust_data["top3_link"] = "https://smart.com.ph/prepaid"

    # Parsing of parameters for top 4 pack
    cust_data["top4_price"] = int(nbo_plans.loc[nbo_plans["Promo"] == cust_data["top4_dpd_lm"], "Srp"].values[0])
    cust_data["top4_validity"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top4_dpd_lm"], "Validity"].values[0]
    cust_data["top4_min"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top4_dpd_lm"], "Voice"].values[0]
    cust_data["top4_sms"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top4_dpd_lm"], "Sms"].values[0]
    cust_data["top4_gb"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top4_dpd_lm"], "Plain Data"].values[0]
    cust_data["top4_app"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top4_dpd_lm"], "Apps"].values[0]
    cust_data["top4_total_app_data"] = nbo_plans.loc[
        nbo_plans["Promo"] == cust_data["top4_dpd_lm"], "Total App Data"
    ].values[0]
    cust_data["top4_total_plain_data"] = nbo_plans.loc[
        nbo_plans["Promo"] == cust_data["top4_dpd_lm"], "Total Plain Data"
    ].values[0]
    cust_data["top4_total_data"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top4_dpd_lm"], "Total Data"].values[0]
    # TODO: replace
    cust_data["top4_link"] = "https://smart.com.ph/prepaid"

    # Parsing of parameters for top 5 pack
    cust_data["top5_price"] = int(nbo_plans.loc[nbo_plans["Promo"] == cust_data["top5_dpd_lm"], "Srp"].values[0])
    cust_data["top5_validity"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top5_dpd_lm"], "Validity"].values[0]
    cust_data["top5_min"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top5_dpd_lm"], "Voice"].values[0]
    cust_data["top5_sms"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top5_dpd_lm"], "Sms"].values[0]
    cust_data["top5_gb"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top5_dpd_lm"], "Plain Data"].values[0]
    cust_data["top5_app"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top5_dpd_lm"], "Apps"].values[0]
    cust_data["top5_total_app_data"] = nbo_plans.loc[
        nbo_plans["Promo"] == cust_data["top5_dpd_lm"], "Total App Data"
    ].values[0]
    cust_data["top5_total_plain_data"] = nbo_plans.loc[
        nbo_plans["Promo"] == cust_data["top5_dpd_lm"], "Total Plain Data"
    ].values[0]
    cust_data["top5_total_data"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["top5_dpd_lm"], "Total Data"].values[0]
    # TODO: replace
    cust_data["top5_link"] = "https://smart.com.ph/prepaid"

    # Parsing of parameters for the last pack the user had
    if cust_data["last_promo"]:
        cust_data["last_pack_price"] = int(
            nbo_plans.loc[nbo_plans["Promo"] == cust_data["last_promo"], "Srp"].values[0]
        )
        cust_data["last_pack_validity"] = nbo_plans.loc[
            nbo_plans["Promo"] == cust_data["last_promo"], "Validity"
        ].values[0]
        cust_data["last_pack_min"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["last_promo"], "Voice"].values[0]
        cust_data["last_pack_sms"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["last_promo"], "Sms"].values[0]
        cust_data["last_pack_gb"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["last_promo"], "Plain Data"].values[0]
        cust_data["last_pack_app"] = nbo_plans.loc[nbo_plans["Promo"] == cust_data["last_promo"], "Apps"].values[0]
        cust_data["last_pack_total_app_data"] = nbo_plans.loc[
            nbo_plans["Promo"] == cust_data["last_promo"], "Total App Data"
        ].values[0]
        cust_data["last_pack_total_plain_data"] = nbo_plans.loc[
            nbo_plans["Promo"] == cust_data["last_promo"], "Total Plain Data"
        ].values[0]
        cust_data["last_pack_total_data"] = nbo_plans.loc[
            nbo_plans["Promo"] == cust_data["last_promo"], "Total Data"
        ].values[0]

    # select & fill opening message
    if cust_data["cust_segment"] == "IncrApp":
        cust_data["opening_message"] = NBO_OFFER_APP
    elif cust_data["cust_segment"] == "IncrOpen":
        cust_data["opening_message"] = NBO_OFFER_OPEN
    elif cust_data["cust_segment"] == "IncrValidity":
        cust_data["opening_message"] = NBO_OFFER_VALIDITY
    else:
        cust_data["opening_message"] = NBO_OFFER_OTHER

    # Dynamic parsing of messages related to the user's last promo
    if cust_data["last_promo"]:
        cust_data["diff_price"] = int(cust_data["top1_price"] - cust_data["last_pack_price"])
        cust_data["price_message"] = f"for only {cust_data['diff_price']} more than your last pack"
        cust_data[
            "last_pack_message"
        ] = f"The user is currently using {cust_data['last_promo']}, which is a a {cust_data['last_pack_validity']} day pack with {cust_data['last_pack_gb']} GB data for a price of {cust_data['last_pack_price']} PHP. The pack has {cust_data['last_pack_min']} minutes of voice and {cust_data['last_pack_sms']} SMS. Also, the pack has {cust_data['last_pack_app']} GB of app data."
    else:
        cust_data["price_message"] = "for a great price"
        cust_data["last_pack_message"] = "The user can find their latest data pack in the Smart app."

    # Parsing of the opening message
    cust_data["opening_message"] = cust_data["opening_message"].format(
        recommended_plan=cust_data["top1_dpd_lm"],
        price_message=cust_data["price_message"],
        upgrade_link=cust_data["top1_link"],
    )
    return cust_data
