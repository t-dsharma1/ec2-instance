from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
import streamlit as st

from connectai.evaluation.visualization.components.state_classification import (
    flow_kpis,
    state_classification_page,
)

# Sample data for testing
data = {
    "Dialogue Flow": ["Flow1", "Flow1", "Flow2"],
    "From State": ["State1", "State2", "State1"],
    "Ground Truth State": ["State1", "State2", "State2"],
    "Evaluation": [0.8, 0.6, 0.9],
}

df = pd.DataFrame(data)


def test_flow_kpis():
    # Pivot table for testing
    pivot_df = pd.pivot_table(df, values="Evaluation", index="From State", columns="Ground Truth State", aggfunc="mean")

    # Expected KPIs
    expected_kpis = (
        pd.DataFrame(
            {
                "Mean": [np.nanmean(pivot_df.values)],
                "Max": [np.nanmax(pivot_df.values)],
                "Min": [np.nanmin(pivot_df.values)],
            },
            index=["Values"],
        )
        .round(2)
        .T
    )

    result_kpis = flow_kpis(pivot_df)

    pd.testing.assert_frame_equal(result_kpis, expected_kpis)


@pytest.fixture
def mock_st():
    with patch("streamlit.session_state", {"state_classification": {"data": data}}), patch(
        "streamlit.tabs", return_value=(MagicMock(), MagicMock())
    ), patch("streamlit.header"), patch("streamlit.columns", return_value=(MagicMock(), MagicMock())), patch(
        "streamlit.dataframe"
    ), patch(
        "streamlit_extras.dataframe_explorer.dataframe_explorer", return_value=df
    ):
        yield


def test_state_classification_page(mock_st):
    state_classification_page()

    # Add assertions to verify expected Streamlit calls
    st.tabs.assert_called_once_with(["Chart 📈", "Detailed Data 📄"])
    st.header.assert_called()
    st.columns.assert_called()
    st.dataframe.assert_called()
