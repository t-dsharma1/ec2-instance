import json
import logging
import os
import pathlib
from operator import itemgetter

import boto3
import streamlit as st
from components import (
    conversation_output_agent_page,
    overview_page,
    state_classification_page,
)
from streamlit_option_menu import option_menu

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# FIXME: Horrible path definition
DEFAULT_RESULTS_PATH = pathlib.Path("../results")


def load_data(
    file_extension: str = "json",
    bucket_name="connectai-atlas-datalake",
    states=["state_classification", "conversation_output_agent"],
):
    path = os.getenv("EVAL_FRAMEWORK_S3_PREFIX", None)
    if path is None:
        for file_path in DEFAULT_RESULTS_PATH.glob("*." + file_extension):
            with open(file_path) as file:
                if file_path.stem not in st.session_state:
                    st.session_state[file_path.stem] = json.load(file)
    else:
        try:
            latest_files = load_latest_files_from_s3(bucket_name, path, suffixes=states)
            logging.info(f"latest files found: {latest_files}")
            s3 = boto3.client("s3")

            for suffix, key in latest_files.items():
                response = s3.get_object(Bucket=bucket_name, Key=key)
                file_content = response["Body"].read()
                data = json.loads(file_content)
                st.session_state[suffix] = data

        except Exception as e:
            st.error(f"Error loading data from S3: {str(e)}")


def load_latest_files_from_s3(bucket_name, path_prefix, suffixes, file_extension: str = "json"):
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=path_prefix)
    filtered_files = {suffix: [] for suffix in suffixes}
    for obj in response.get("Contents", []):
        for suffix in suffixes:
            if obj["Key"].endswith(f"_{suffix}.{file_extension}"):
                filtered_files[suffix].append({"key": obj["Key"], "last_modified": obj["LastModified"]})

    latest_files = {}
    for suffix, files in filtered_files.items():
        if files:
            latest_files[suffix] = max(files, key=itemgetter("last_modified"))["key"]

    return latest_files


def main():
    st.set_page_config(
        page_title="Evaluation Dashboard",
        page_icon="📊",
        layout="wide",
    )
    # = Load evaluation data =#
    load_data()

    # = Navigation Bar =#
    with st.sidebar:
        page = option_menu(
            "Evaluation",
            ["Overview", "Conversation Output Agent", "State Classification"],
            icons=["card-list", "chat-left-text", "funnel"],
            menu_icon="list",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#F0F2F6"},
            },
        )

    if page == "Overview":
        overview_page()
    elif page == "State Classification":
        state_classification_page()
    elif page == "Conversation Output Agent":
        conversation_output_agent_page()


if __name__ == "__main__":
    main()
