import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer


def state_classification_page():
    data = pd.DataFrame(st.session_state["state_classification"]["data"])

    tab1, tab2 = st.tabs(["Chart 📈", "Detailed Data 📄"])

    with tab1:
        for flow in data["Dialogue Flow"].unique():
            st.header(f"Dialogue Flow: {flow}")
            col1, col2 = st.columns(2, gap="large")
            df = data[data["Dialogue Flow"] == flow]
            pivot_df = pd.pivot_table(
                df, values="Evaluation", index="From State", columns="Ground Truth State", aggfunc="mean"
            )
            fig = px.imshow(
                pivot_df.values,
                x=pivot_df.columns.tolist(),
                y=pivot_df.index.tolist(),
                color_continuous_scale="Sunset",
                aspect="auto",
                text_auto=".2f",
            )
            # Updating layout for clarity
            fig.update_layout(
                xaxis_title="To State",
                yaxis_title="From State",
                xaxis_showgrid=False,
                yaxis_showgrid=False,
                xaxis=dict(
                    tickvals=list(range(len(pivot_df.columns.tolist()))),
                    ticktext=pivot_df.columns.tolist(),
                    side="bottom",
                ),
            )
            col1.write(fig)
            col2.dataframe(flow_kpis(pivot_df), use_container_width=False)

    with tab2:
        # TODO: Update graph according to filters
        filtered_df = dataframe_explorer(data, case=False)
        st.dataframe(filtered_df, use_container_width=True)


def flow_kpis(df) -> pd.DataFrame:
    return (
        pd.DataFrame(
            {
                "Mean": [np.nanmean(df)],
                "Max": [np.nanmax(df)],
                "Min": [np.nanmin(df)],
            },
            index=["Values"],
        )
        .round(2)
        .T
    )
