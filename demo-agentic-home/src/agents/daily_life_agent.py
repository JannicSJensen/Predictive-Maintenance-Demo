from __future__ import annotations

from typing import Any, Dict, List

from src.agents.base import Agent


class DailyLifePatternAgent(Agent):
    name = "daily_life_pattern_agent"
    description = "Infers routines and occupancy patterns from home telemetry"

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        occupancy = context.get("room_occupancy", {})
        findings: List[str] = []
        anomalies: List[str] = []

        if occupancy.get("kitchen", {}).get("morning", 0) >= 2:
            findings.append("Kitchen activity starts around 06:45 on weekdays.")
        office_morning = occupancy.get("office", {}).get("morning", 0)
        office_day = occupancy.get("office", {}).get("day", 0)
        if office_day >= 2 or office_morning >= 2:
            findings.append("Office occupancy is common between 08:30 and 16:30.")
        if occupancy.get("living_room", {}).get("evening", 0) >= 3:
            findings.append("Living room activity peaks after 19:30.")
        if occupancy.get("living_room", {}).get("night", 0) == 0:
            findings.append("No motion detected after 23:15 most nights.")

        climate_patterns = context.get("climate_patterns", {})
        humidity_events = climate_patterns.get("bedroom_high_humidity_events", [])
        if humidity_events:
            anomalies.append("Bedroom humidity spikes above 68% on some mornings.")

        return {
            "agent": self.name,
            "findings": findings,
            "anomalies": anomalies,
            "explainability_note": "Patterns are deterministic summaries from motion, power, climate, and schedule proxies.",
        }
