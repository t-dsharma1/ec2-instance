from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

__all__ = ["Customer", "CustomerInformation"]


@dataclass_json
@dataclass
class Customer:
    name: Optional[str] = None
    elements: Optional[list] = None


@dataclass_json
@dataclass
class CustomerInformation:
    # Basic customer info
    star_status: Optional[str] = None
    no_of_month: Optional[float] = None
    customer_segment: Optional[str] = None
    targeted_30day_pack: Optional[float] = None

    # Data balances and expiry
    remaining_gb: Optional[float] = None
    expiry_in_next_3_days: Optional[float] = None

    # Historical recharge values
    avg_recharge_m1: Optional[float] = None
    avg_recharge_m2: Optional[float] = None
    avg_recharge_m3: Optional[float] = None

    # Historical data usage
    avg_gb_m1: Optional[float] = None
    avg_gb_m2: Optional[float] = None
    avg_gb_m3: Optional[float] = None

    # Historical pack purchase hits
    pack_purchase_hit_m1: Optional[float] = None
    pack_purchase_hit_m2: Optional[float] = None
    pack_purchase_hit_m3: Optional[float] = None

    # Historical pack purchase revenues
    pack_purchase_revenue_m1: Optional[float] = None
    pack_purchase_revenue_m2: Optional[float] = None
    pack_purchase_revenue_m3: Optional[float] = None

    # Information about recent packs
    last_pack_min: Optional[float] = None
    last_pack_price: Optional[float] = None
    last_pack_gb: Optional[float] = None
    last_pack_validity: Optional[float] = None

    @classmethod
    def load(cls, data_dict: dict):
        flattened_dict = {
            item["parameter_name"].replace(" ", "_").lower(): item["parameter_value"]
            for element in data_dict["elements"]
            for item in element["parameter_data"]
        }

        return cls.from_dict(flattened_dict)
