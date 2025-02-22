import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards


def overview_page():
    with st.container(border=True):
        st.markdown("#### Conversational Agent", help="")
        with st.container(border=True):
            n_samples = st.session_state["conversation_output_agent"]["kpi"]["coupled"]["no_test_cases"]
            st.markdown(f"##### Coupled (n={n_samples})")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric(
                label="Business Logic",
                value=st.session_state["conversation_output_agent"]["kpi"]["coupled"]["average"]["Business Logic Eval"],
                help="Assesses if the LLM aligns with business goals, using the correct commercial language and sales tactics",
            )
            col2.metric(
                label="Faithfullness",
                value=st.session_state["conversation_output_agent"]["kpi"]["coupled"]["average"]["Faithfullness Eval"],
                help="Measures the LLM's accuracy, ensuring it provides true information without fabricating data (hallucinations)",
            )
            col3.metric(
                label="Relevance",
                value=st.session_state["conversation_output_agent"]["kpi"]["coupled"]["average"]["Relevance Eval"],
                help="Evaluates whether the LLM's responses are pertinent and useful, based on the context or inquiry.",
            )
            col4.metric(
                label="RAI",
                value=st.session_state["conversation_output_agent"]["kpi"]["coupled"]["average"]["RAI Eval"],
                help="Checks the LLM for ethical compliance, preventing harmful or inappropriate content.",
            )
            col5.metric(
                label="Llama Guard",
                value=st.session_state["conversation_output_agent"]["kpi"]["coupled"]["average"]["Llama Guard Eval"],
                help="Llama Guard safe/unsafe classification",
            )

        with st.container(border=True):
            n_samples = st.session_state["conversation_output_agent"]["kpi"]["decoupled"]["no_test_cases"]
            st.markdown(f"##### Decoupled (n={n_samples})")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(
                label="Faithfullness",
                value=st.session_state["conversation_output_agent"]["kpi"]["decoupled"]["average"][
                    "Faithfullness Eval"
                ],
                help="Measures the LLM's accuracy, ensuring it provides true information without fabricating data (hallucinations)",
            )
            col2.metric(
                label="Relevance",
                value=st.session_state["conversation_output_agent"]["kpi"]["decoupled"]["average"]["Relevance Eval"],
                help="Evaluates whether the LLM's responses are pertinent and useful, based on the context or inquiry.",
            )
            col3.metric(
                label="RAI",
                value=st.session_state["conversation_output_agent"]["kpi"]["decoupled"]["average"]["RAI Eval"],
                help="Checks the LLM for ethical compliance, preventing harmful or inappropriate content.",
            )
            col4.metric(
                label="Llama Guard",
                value=st.session_state["conversation_output_agent"]["kpi"]["decoupled"]["average"]["Llama Guard Eval"],
                help="Llama Guard safe/unsafe classification",
            )

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1.container(border=True):
        n_samples = st.session_state["state_classification"]["kpi"]["no_test_cases"]
        st.markdown(f"#### State classification (n={n_samples})", help="")
        col11, col22 = st.columns(2)
        col11.metric(label="Average", value=st.session_state["state_classification"]["kpi"]["average"], help="")
        col22.metric(label="Min", value=st.session_state["state_classification"]["kpi"]["min"], help="")

    style_metric_cards(border_left_color="#387FF3")
