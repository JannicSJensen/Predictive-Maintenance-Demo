from __future__ import annotations

from typing import Any, Dict, List

from src.agents.base import Agent
from src.models.recommendations import Recommendation


class ClimateAgent(Agent):
    name = "climate_agent"
    description = "Balances climate comfort and energy using occupancy and telemetry context"

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        recommendations: List[Recommendation] = []
        climate_patterns = context.get("climate_patterns", {})

        recommendations.append(
            Recommendation(
                id="rec_climate_01",
                agent_name=self.name,
                type="climate",
                title="Align office pre-heat with occupancy probability",
                rationale="Office heating starts before occupancy; delay warm-up to reduce waste.",
                evidence=[
                    "office preheat occurs before office motion",
                    f"detected preheat-before-motion events: {climate_patterns.get('office_preheat_before_motion_events', 0)}",
                ],
                risk_level="medium",
                requires_approval=True,
                proposed_action={"entity": "climate.office", "schedule": "weekdays_08_15"},
                yaml=None,
            )
        )

        if climate_patterns.get("bedroom_high_humidity_events"):
            recommendations.append(
                Recommendation(
                    id="rec_climate_02",
                    agent_name=self.name,
                    type="climate",
                    title="Trigger ventilation alert on high morning bedroom humidity",
                    rationale="Humidity above healthy comfort range may impact comfort and air quality.",
                    evidence=["bedroom humidity exceeded 68% on multiple mornings"],
                    risk_level="low",
                    requires_approval=False,
                    proposed_action={"entity": "sensor.bedroom_humidity", "service": "notify"},
                    yaml=None,
                )
            )

        return {
            "agent": self.name,
            "recommendations": recommendations,
        }
