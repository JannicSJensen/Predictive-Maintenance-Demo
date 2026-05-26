from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from src.agents.orchestrator import HomeIntelligenceOrchestrator
from src.agents.safety_agent import SafetyAgent
from src.connectors.azure_event_hub import AzureEventHubConnector
from src.connectors.fabric_memory import FabricMemoryConnector
from src.connectors.home_assistant import HomeAssistantConnector


class HomeIntelligenceWorkflow:
    def __init__(self, project_root: Path) -> None:
        sample_events_path = project_root / "src" / "sample_data" / "home_assistant_events.json"
        filter_config_path = project_root / "src" / "config" / "home_assistant_azure_event_hub_example.yaml"
        safety_policy_path = project_root / "src" / "config" / "safety_policy.yaml"

        envelope_store_path = project_root / "data" / "event_hub_envelopes.json"
        fabric_events_path = project_root / "data" / "fabric_events.json"
        recommendations_path = project_root / "data" / "agent_recommendations.json"

        self.home_assistant = HomeAssistantConnector(sample_events_path, filter_config_path)
        self.event_hub = AzureEventHubConnector(envelope_store_path)
        self.fabric_memory = FabricMemoryConnector(fabric_events_path, recommendations_path)
        self.orchestrator = HomeIntelligenceOrchestrator(SafetyAgent(safety_policy_path))

    def run(self) -> Dict[str, Any]:
        question = "What does daily life look like in this home, and what automations would improve comfort and energy usage?"

        # Reset local stores so each demo run is deterministic and easy to explain.
        for path in [
            self.event_hub.envelope_store_path,
            self.fabric_memory.event_store_path,
            self.fabric_memory.recommendations_path,
        ]:
            if path.exists():
                path.unlink()

        raw_events = self.home_assistant.get_event_bus_sample()
        filtered_events = self.home_assistant.filter_events_for_event_hub(raw_events)
        published = self.event_hub.publish_batch(filtered_events)
        consumed = self.event_hub.consume_events()

        self.fabric_memory.ingest_event_hub_envelopes(consumed)

        daily_summary = self.fabric_memory.query_daily_summary()
        room_occupancy = self.fabric_memory.query_room_occupancy()
        energy_usage = self.fabric_memory.query_energy_usage()
        climate_patterns = self.fabric_memory.query_climate_patterns()

        orchestration_result = self.orchestrator.run(
            {
                "goal": question,
                "daily_summary": daily_summary,
                "room_occupancy": room_occupancy,
                "energy_usage": energy_usage,
                "climate_patterns": climate_patterns,
                "event_hub_ingestion_summary": self.event_hub.get_ingestion_summary(),
            }
        )

        for recommendation in orchestration_result.get("recommendations", []):
            # Save trace of generated recommendations in local memory layer.
            from src.models.recommendations import Recommendation

            self.fabric_memory.save_agent_recommendation(Recommendation(**recommendation))

        home_activity_summary = self._build_home_activity_summary(room_occupancy, energy_usage, climate_patterns)
        architecture_recap = self._build_architecture_recap()
        automation_yamls = self._collect_yaml(orchestration_result.get("recommendations", []), rec_type="automation")

        return {
            "sequence": {
                "loaded_events": len(raw_events),
                "filtered_events": len(filtered_events),
                "published_envelopes": len(published),
                "consumed_envelopes": len(consumed),
            },
            "orchestrator_question": question,
            "event_hub_ingestion_summary": self.event_hub.get_ingestion_summary(),
            "home_activity_summary": home_activity_summary,
            "orchestration": orchestration_result,
            "generated_automation_yaml": automation_yamls,
            "generated_dashboard_yaml": orchestration_result.get("generated_dashboard_yaml"),
            "architecture_recap": architecture_recap,
        }

    @staticmethod
    def _build_home_activity_summary(
        room_occupancy: Dict[str, Dict[str, int]],
        energy_usage: Dict[str, Any],
        climate_patterns: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "occupancy_patterns": room_occupancy,
            "energy_snapshot": energy_usage,
            "climate_snapshot": climate_patterns,
            "highlights": [
                "Morning kitchen activity is consistent.",
                "Office occupancy is mostly daytime.",
                "Living room activity peaks in the evening.",
                "Overnight media standby appears repeatedly.",
            ],
        }

    @staticmethod
    def _build_architecture_recap() -> List[str]:
        return [
            "Home Assistant provides the operational environment.",
            "Azure Event Hub connector simulates ingestion and envelope semantics.",
            "Fabric memory connector stores and queries telemetry context.",
            "Foundry-style orchestration runs specialized deterministic agents.",
            "Safety and evaluation guardrails stage decisions before execution.",
        ]

    @staticmethod
    def _collect_yaml(recommendations: List[Dict[str, Any]], rec_type: str) -> List[str]:
        return [rec["yaml"] for rec in recommendations if rec.get("type") == rec_type and rec.get("yaml")]
