from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.workflows.home_intelligence_workflow import HomeIntelligenceWorkflow


st.set_page_config(page_title="Agentic Home Demo", layout="wide")
st.title("Agentic Smart-Home Architecture Demo")
st.caption("Local-first Home Assistant + Azure Event Hub + Fabric + Foundry-style agents")

if st.button("Run Demo"):
    project_root = Path(__file__).resolve().parents[2]
    workflow = HomeIntelligenceWorkflow(project_root)
    result = workflow.run()

    st.subheader("Azure Event Hub ingestion summary")
    st.json(result["event_hub_ingestion_summary"])

    st.subheader("Home activity summary")
    st.json(result["home_activity_summary"])

    st.subheader("Agent findings")
    st.json(result["orchestration"]["daily_life_summary"])

    st.subheader("Recommendations")
    st.json(result["orchestration"]["recommendations"])

    st.subheader("Safety review")
    st.json(result["orchestration"]["safety_review"])

    st.subheader("Evaluation scores")
    st.json(result["orchestration"]["evaluation_scores"])

    st.subheader("Generated Home Assistant YAML")
    for yaml_def in result["generated_automation_yaml"]:
        st.code(yaml_def, language="yaml")

    st.subheader("Generated Lovelace dashboard YAML")
    st.code(result["generated_dashboard_yaml"], language="yaml")

    st.subheader("Demo architecture recap")
    for line in result["architecture_recap"]:
        st.write(f"- {line}")
else:
    st.info("Click 'Run Demo' to execute the full local deterministic workflow.")
