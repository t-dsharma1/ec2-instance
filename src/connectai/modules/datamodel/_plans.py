from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class ProductContext:
    product_subset: list[str]
    # TODO: determine if this is enough or should be extended. Question is, how do we plan to pass the 'static_info'
    # TODO: for our flow context?
