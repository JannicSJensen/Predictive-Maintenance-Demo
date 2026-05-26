from __future__ import annotations

from typing import Any, Dict, List

from src.agents.base import Agent
from src.models.recommendations import Recommendation


class EnergyAgent(Agent):
    name = "energy_agent"
    description = "Finds practical low-risk home energy optimizations"

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        recommendations: List[Recommendation] = []
        energy_usage = context.get("energy_usage", {})

        recommendations.append(
            Recommendation(
                id="rec_energy_01",
                agent_name=self.name,
                type="energy",
                title="Cut media-center standby consumption overnight",
                rationale="Standby events appear repeatedly during overnight low-activity periods.",
                evidence=[
                    f"standby media events: {energy_usage.get('standby_media_events', 0)}",
                    "low motion after 23:15",
                ],
                risk_level="low",
                requires_approval=True,
                proposed_action={"entity": "switch.media_center", "service": "switch.turn_off", "window": "00:15-06:00"},
                yaml=None,
            )
        )

        recommendations.append(
            Recommendation(
                id="rec_energy_02",
                agent_name=self.name,
                type="energy",
                title="Shift discretionary loads to low-price periods",
                rationale="Energy tariff periods can be used for simple demand shifting.",
                evidence=[
                    "sensor.grid_energy_price telemetry present",
                    f"average power draw: {energy_usage.get('average_power_w', 0)}W",
                ],
                risk_level="low",
                requires_approval=False,
                proposed_action={"entity": "sensor.grid_energy_price", "strategy": "delay_non_critical_loads"},
                yaml=None,
            )
        )

        return {
            "agent": self.name,
            "recommendations": recommendations,
        }
