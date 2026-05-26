from __future__ import annotations

import json
from pathlib import Path

from src.workflows.home_intelligence_workflow import HomeIntelligenceWorkflow


def _print_section(title: str) -> None:
    print(f"\n{'=' * 12} {title} {'=' * 12}")


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    workflow = HomeIntelligenceWorkflow(project_root)
    result = workflow.run()

    _print_section("Orchestrator question")
    print(result["orchestrator_question"])

    _print_section("Azure Event Hub ingestion summary")
    print(json.dumps(result["event_hub_ingestion_summary"], indent=2))

    _print_section("Home activity summary")
    print(json.dumps(result["home_activity_summary"], indent=2))

    _print_section("Agent findings")
    print(json.dumps(result["orchestration"]["daily_life_summary"], indent=2))

    _print_section("Recommendations")
    print(json.dumps(result["orchestration"]["recommendations"], indent=2))

    _print_section("Safety review")
    print(json.dumps(result["orchestration"]["safety_review"], indent=2))

    _print_section("Evaluation scores")
    print(json.dumps(result["orchestration"]["evaluation_scores"], indent=2))

    _print_section("Generated Home Assistant YAML")
    for idx, yaml_def in enumerate(result["generated_automation_yaml"], start=1):
        print(f"\n# Automation {idx}\n{yaml_def}")

    _print_section("Generated Lovelace dashboard YAML")
    print(result["generated_dashboard_yaml"])

    _print_section("Demo architecture recap")
    for line in result["architecture_recap"]:
        print(f"- {line}")


if __name__ == "__main__":
    main()
