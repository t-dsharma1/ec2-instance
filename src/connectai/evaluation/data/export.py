from datetime import datetime

import pandas as pd

from connectai.evaluation.factory.test_factory import TestFactory


def export_to_excel(base_filename: str, **data_dicts):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{base_filename}_{timestamp}.xlsx"

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        for dict_name, data_dict in data_dicts.items():
            for sheet_name, data in data_dict.items():
                df = pd.DataFrame(data).rename(columns={0: sheet_name})
                full_sheet_name = f"{dict_name.upper()} {sheet_name}"
                df.to_excel(writer, sheet_name=full_sheet_name, index=False)


if __name__ == "__main__":
    test_factory = TestFactory()
    export_to_excel(
        "test_data", test=test_factory.test_cases, flow=test_factory.flows, messages=test_factory.user_messages
    )
