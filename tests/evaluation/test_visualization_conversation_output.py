from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import streamlit as st

from connectai.evaluation.visualization.components.conversation_output_agent import (
    conversation_output_agent_page,
)

data = {
    "RAI Eval": ["No", "Yes", "No", "Yes"],
    "Llama Guard Eval": ["safe", "unsafe", "safe", "unsafe"],
    "Business Logic": [None, "Logic1", "Logic2", None],
    "Business Logic Eval": ["Yes", "No", "Yes", "No"],
    "Faithfullness Eval": ["Yes", "No", "Yes", "No"],
    "Relevance Eval": ["Yes", "No", "Yes", "No"],
}

df = pd.DataFrame(data)


@pytest.fixture
def mock_st():
    with patch("streamlit.session_state", {"conversation_output_agent": {"data": data}}), patch(
        "streamlit.tabs", return_value=(MagicMock(), MagicMock())
    ), patch("streamlit.header"), patch("streamlit.columns", return_value=(MagicMock(), MagicMock())), patch(
        "streamlit.dataframe"
    ), patch(
        "streamlit_extras.dataframe_explorer.dataframe_explorer", return_value=df
    ):
        yield


def test_conversation_output_agent_page(mock_st):
    conversation_output_agent_page()

    st.tabs.assert_called_once_with(["Chart 📈", "Detailed Data 📄"])
    st.columns.assert_called()
    st.dataframe.assert_called()
