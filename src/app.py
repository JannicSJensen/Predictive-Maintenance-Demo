import os
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from agents import AgentOutput, run_multi_agent_pipeline
from factory_mapping import map_recommendation_to_factory, mapping_table_rows
from home_assistant_client import load_client_from_env

load_dotenv()


st.set_page_config(page_title="Agentic AI: Home to Factory Demo", layout="wide")
st.title("Agentic AI Demo: Smart Home to Predictive Maintenance")
st.caption("Home Assistant as a miniature operations environment")


@st.cache_data(ttl=30)
def get_states() -> List[Dict[str, Any]]:
    client = load_client_from_env()
    return client.states()


def render_agent_outputs(outputs: List[AgentOutput]) -> None:
    for output in outputs:
        with st.expander(output.name, expanded=True):
            st.write(output.summary)
            if output.details:
                st.json(output.details)


def render_recommendations(outputs: List[AgentOutput]) -> None:
    rec_output = next((o for o in outputs if o.name == "Recommendation Agent"), None)
    if not rec_output:
        return

    recommendations = rec_output.details.get("recommendations", [])
    if not recommendations:
        st.info("No recommendations generated.")
        return

    st.subheader("Recommended actions")
    rec_df = pd.DataFrame(recommendations)
    st.dataframe(rec_df, use_container_width=True)

    st.subheader("Factory translation")
    factory_rows = [map_recommendation_to_factory(r) for r in recommendations]
    st.dataframe(pd.DataFrame(factory_rows), use_container_width=True)

    st.subheader("Human approval gate")
    selected = st.selectbox(
        "Select recommendation to approve",
        options=list(range(len(recommendations))),
        format_func=lambda i: recommendations[i]["title"],
    )
    approved = st.checkbox("I approve this action for execution")
    if approved:
        st.success(
            f"Approved: {recommendations[selected]['title']} at {datetime.now().strftime('%H:%M:%S')}"
        )
    else:
        st.warning("Awaiting human approval")


def render_mapping_table() -> None:
    st.subheader("Architecture mapping")
    st.dataframe(pd.DataFrame(mapping_table_rows()), use_container_width=True)


with st.sidebar:
    st.header("Configuration")
    st.write(f"HA_URL: {os.getenv('HA_URL', '(not set)')}")
    token_set = "yes" if os.getenv("HA_TOKEN") else "no"
    st.write(f"HA_TOKEN set: {token_set}")

    run_button = st.button("Run multi-agent analysis", type="primary")


col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live system state")
    try:
        states = get_states()
        state_df = pd.DataFrame(
            [
                {
                    "entity_id": s.get("entity_id"),
                    "state": s.get("state"),
                    "last_changed": s.get("last_changed"),
                }
                for s in states
            ]
        )
        st.dataframe(state_df, use_container_width=True, height=360)
    except Exception as exc:
        states = []
        st.error(f"Could not read Home Assistant states: {exc}")
        st.info("Set HA_URL and HA_TOKEN in .env and rerun.")

with col2:
    render_mapping_table()

if run_button:
    if not states:
        st.error("No sensor state available for analysis.")
    else:
        outputs = run_multi_agent_pipeline(states)
        st.header("Agent workflow output")
        render_agent_outputs(outputs)
        render_recommendations(outputs)
else:
    st.info("Click 'Run multi-agent analysis' to execute the demo workflow.")
