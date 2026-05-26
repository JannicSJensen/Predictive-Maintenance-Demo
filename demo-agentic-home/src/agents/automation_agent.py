from __future__ import annotations

from typing import Any, Dict, List

import yaml

from src.agents.base import Agent
from src.models.recommendations import Recommendation


class AutomationAgent(Agent):
    name = "automation_agent"
    description = "Generates practical and reversible Home Assistant automations"

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        recommendations: List[Recommendation] = []

        hallway_automation = {
            "alias": "Turn off hallway light after no motion at night",
            "trigger": [{"platform": "state", "entity_id": "binary_sensor.kitchen_motion", "to": "off", "for": "00:08:00"}],
            "condition": [{"condition": "time", "after": "22:00:00"}],
            "action": [{"service": "light.turn_off", "target": {"entity_id": "light.hallway"}}],
            "mode": "single",
        }
        recommendations.append(
            Recommendation(
                id="rec_auto_01",
                agent_name=self.name,
                type="automation",
                title="Night hallway light auto-off",
                rationale="Hallway light is occasionally left on late at night without nearby motion.",
                evidence=["light.hallway stayed on after 22:30 on multiple days", "low motion activity after 23:15"],
                risk_level="low",
                requires_approval=True,
                proposed_action={"entity": "light.hallway", "service": "light.turn_off"},
                yaml=yaml.safe_dump(hallway_automation, sort_keys=False),
            )
        )

        heating_window_alert = {
            "alias": "Notify if heating is active while a window remains open",
            "trigger": [{"platform": "state", "entity_id": "climate.office", "to": "heat"}],
            "condition": [{"condition": "state", "entity_id": "binary_sensor.office_window", "state": "on"}],
            "action": [{"service": "notify.mobile_app", "data": {"message": "Office window open while heating is active."}}],
            "mode": "single",
        }
        recommendations.append(
            Recommendation(
                id="rec_auto_02",
                agent_name=self.name,
                type="automation",
                title="Heating-and-window conflict alert",
                rationale="Prevent avoidable heating loss and occupant surprise.",
                evidence=["office heating starts before occupancy window", "energy peak around early office warm-up"],
                risk_level="low",
                requires_approval=True,
                proposed_action={"entity": "climate.office", "service": "notify"},
                yaml=yaml.safe_dump(heating_window_alert, sort_keys=False),
            )
        )

        away_mode_suggestion = {
            "alias": "Suggest away mode after prolonged inactivity",
            "trigger": [{"platform": "state", "entity_id": "binary_sensor.living_room_motion", "to": "off", "for": "03:00:00"}],
            "condition": [{"condition": "state", "entity_id": "switch.media_center", "state": "on"}],
            "action": [{"service": "notify.mobile_app", "data": {"message": "No activity detected for 3 hours. Suggest enabling away mode."}}],
            "mode": "single",
        }
        recommendations.append(
            Recommendation(
                id="rec_auto_03",
                agent_name=self.name,
                type="automation",
                title="Away mode suggestion after inactivity",
                rationale="Long inactivity windows suggest opportunities for manual away-mode activation.",
                evidence=["overnight motion inactivity", "media center standby events after midnight"],
                risk_level="low",
                requires_approval=True,
                proposed_action={"entity": "home", "service": "notify"},
                yaml=yaml.safe_dump(away_mode_suggestion, sort_keys=False),
            )
        )

        return {
            "agent": self.name,
            "recommendations": recommendations,
        }
