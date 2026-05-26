from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from src.models.recommendations import Recommendation
from src.models.serialization import model_to_dict
from src.models.telemetry import EventHubEnvelope, TelemetryEvent


class FabricMemoryConnector:
    """Local Fabric-style memory layer using JSON storage.

    TODO: Replace with Microsoft Fabric Eventstream/Lakehouse/KQL integrations.
    """

    def __init__(self, event_store_path: Path, recommendations_path: Path) -> None:
        self.event_store_path = event_store_path
        self.recommendations_path = recommendations_path
        self.event_store_path.parent.mkdir(parents=True, exist_ok=True)

    def ingest_event_hub_envelopes(self, envelopes: List[EventHubEnvelope]) -> int:
        events = [model_to_dict(envelope.payload) for envelope in envelopes]
        with self.event_store_path.open("w", encoding="utf-8") as f:
            json.dump(events, f, indent=2, default=str)
        return len(events)

    def load_events(self) -> List[TelemetryEvent]:
        if not self.event_store_path.exists():
            return []
        with self.event_store_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        return [TelemetryEvent(**event) for event in raw]

    def query_daily_summary(self) -> Dict[str, object]:
        events = self.load_events()
        by_day = Counter(event.timestamp.date().isoformat() for event in events)
        by_domain = Counter(event.domain for event in events)
        return {
            "days_observed": sorted(by_day.keys()),
            "events_per_day": dict(by_day),
            "events_by_domain": dict(by_domain),
            "total_events": len(events),
        }

    def query_room_occupancy(self) -> Dict[str, Dict[str, int]]:
        events = self.load_events()
        occupancy: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for event in events:
            if event.domain == "binary_sensor" and "motion" in event.entity_id and event.state == "on" and event.room:
                bucket = self._time_bucket(event.timestamp)
                occupancy[event.room][bucket] += 1
        return {room: dict(buckets) for room, buckets in occupancy.items()}

    def query_energy_usage(self) -> Dict[str, object]:
        events = self.load_events()
        power_values = []
        night_media_standby = 0
        for event in events:
            if event.entity_id == "sensor.home_power_consumption":
                try:
                    power_values.append(float(event.state))
                except ValueError:
                    continue
            if event.entity_id == "switch.media_center" and event.attributes.get("standby"):
                night_media_standby += 1

        avg_power = round(sum(power_values) / len(power_values), 1) if power_values else 0.0
        peak_power = max(power_values) if power_values else 0.0

        return {
            "average_power_w": avg_power,
            "peak_power_w": peak_power,
            "standby_media_events": night_media_standby,
        }

    def query_climate_patterns(self) -> Dict[str, object]:
        events = self.load_events()
        humidity_peaks = []
        office_preheat_before_motion = 0
        office_motion_times = [e.timestamp for e in events if e.entity_id == "binary_sensor.office_motion" and e.state == "on"]

        for event in events:
            if event.entity_id == "sensor.bedroom_humidity":
                try:
                    value = float(event.state)
                    if value >= 68:
                        humidity_peaks.append({"timestamp": event.timestamp.isoformat(), "humidity": value})
                except ValueError:
                    continue

            if event.entity_id == "climate.office" and office_motion_times:
                if any((motion_time - event.timestamp).total_seconds() > 0 and (motion_time - event.timestamp).total_seconds() < 1200 for motion_time in office_motion_times):
                    office_preheat_before_motion += 1

        return {
            "bedroom_high_humidity_events": humidity_peaks,
            "office_preheat_before_motion_events": office_preheat_before_motion,
        }

    def save_agent_recommendation(self, recommendation: Recommendation) -> None:
        if self.recommendations_path.exists():
            with self.recommendations_path.open("r", encoding="utf-8") as f:
                current = json.load(f)
        else:
            current = []

        current.append(model_to_dict(recommendation))
        with self.recommendations_path.open("w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, default=str)

    @staticmethod
    def _time_bucket(timestamp: datetime) -> str:
        hour = timestamp.hour
        if 5 <= hour < 11:
            return "morning"
        if 11 <= hour < 17:
            return "day"
        if 17 <= hour < 23:
            return "evening"
        return "night"
