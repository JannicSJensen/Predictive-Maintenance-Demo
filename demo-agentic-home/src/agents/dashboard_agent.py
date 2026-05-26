from __future__ import annotations

from typing import Any, Dict

import yaml

from src.agents.base import Agent
from src.models.recommendations import Recommendation


class DashboardBuilderAgent(Agent):
    name = "dashboard_builder_agent"
    description = "Builds Lovelace dashboard YAML for demo storytelling"

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        dashboard = {
            "title": "Agentic Home Intelligence",
            "views": [
                {
                    "title": "Overview",
                    "path": "overview",
                    "cards": [
                        {"type": "entities", "title": "Home Status Overview", "entities": ["sensor.home_power_consumption", "sensor.grid_energy_price", "climate.office", "climate.living_room"]},
                        {"type": "entities", "title": "Room Comfort", "entities": ["sensor.office_temperature", "sensor.living_room_temperature", "sensor.bedroom_humidity"]},
                    ],
                },
                {
                    "title": "Agent Ops",
                    "path": "agent_ops",
                    "cards": [
                        {"type": "markdown", "title": "Agent Recommendations", "content": "See generated recommendations and safety decisions in demo output."},
                        {"type": "markdown", "title": "Pending Approvals", "content": "Climate and automation changes requiring manual confirmation."},
                        {"type": "markdown", "title": "Automation Impact", "content": "Expected reduction in standby and unnecessary heating usage."},
                    ],
                },
            ],
        }

        rec = Recommendation(
            id="rec_dashboard_01",
            agent_name=self.name,
            type="dashboard",
            title="Create agentic home operations dashboard",
            rationale="Unify telemetry, recommendations, and approvals in one presentation-friendly view.",
            evidence=["energy, climate, occupancy, and recommendation streams available"],
            risk_level="low",
            requires_approval=False,
            proposed_action={"target": "lovelace"},
            yaml=yaml.safe_dump(dashboard, sort_keys=False),
        )

        return {
            "agent": self.name,
            "recommendations": [rec],
            "dashboard_yaml": rec.yaml,
        }
