import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer


def conversation_output_agent_page():
    data = pd.DataFrame(st.session_state["conversation_output_agent"]["data"])

    tab1, tab2 = st.tabs(["Chart 📈", "Detailed Data 📄"])

    with tab1:
        data["RAI Eval"] = data["RAI Eval"].str.replace("No", "Yes")
        data["Llama Guard Eval"] = data["Llama Guard Eval"].str.replace("safe", "Yes")

        coupled = data.dropna(subset=["Business Logic"]).copy()
        decoupled = data[data["Business Logic"].isna()].copy()

        col1, col2 = st.columns(2, gap="large")
        col1.header("Coupled")
        col2.header("Decoupled")
        accuracy_coupled = (
            (coupled[["Business Logic Eval", "Faithfullness Eval", "Relevance Eval", "RAI Eval"]] == "Yes")
            .mean()
            .reset_index()
        )
        accuracy_decoupled = (
            (decoupled[["Faithfullness Eval", "Relevance Eval", "RAI Eval"]] == "Yes").mean().reset_index()
        )

        accuracy_coupled.columns = ["Metric", "Average"]
        accuracy_decoupled.columns = ["Metric", "Average"]

        fig = px.bar(accuracy_coupled, x="Metric", y="Average", text="Average")
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_yaxes(tickformat=".2f")
        fig.update_traces(marker_color="#387FF3")
        fig.update_layout(xaxis=dict(tickfont=dict(size=16)), yaxis=dict(tickfont=dict(size=16)))
        col1.write(fig)

        fig = px.bar(accuracy_decoupled, x="Metric", y="Average", text="Average")
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_yaxes(tickformat=".2f")
        fig.update_traces(marker_color="#387FF3")
        fig.update_layout(xaxis=dict(tickfont=dict(size=16)), yaxis=dict(tickfont=dict(size=16)))
        col2.write(fig)

    with tab2:
        # TODO: Update graph according to filters
        filtered_df = dataframe_explorer(data, case=False)
        st.dataframe(filtered_df, use_container_width=True)
