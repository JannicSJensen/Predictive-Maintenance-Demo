from __future__ import annotations

import fnmatch
import json
from pathlib import Path
from typing import Any, Dict, List

import yaml

from src.models.telemetry import TelemetryEvent


class HomeAssistantConnector:
    """Local/mock Home Assistant connector.

    TODO: Replace with real Home Assistant REST/WebSocket API integration.
    """

    def __init__(self, sample_events_path: Path, filter_config_path: Path) -> None:
        self.sample_events_path = sample_events_path
        self.filter_config_path = filter_config_path

    def get_states(self) -> List[Dict[str, Any]]:
        events = self.get_event_bus_sample()
        latest: Dict[str, Dict[str, Any]] = {}
        for event in events:
            latest[event.entity_id] = {
                "entity_id": event.entity_id,
                "state": event.state,
                "attributes": event.attributes,
                "timestamp": event.timestamp.isoformat(),
            }
        return list(latest.values())

    def get_history(self) -> List[TelemetryEvent]:
        return self.get_event_bus_sample()

    def get_event_bus_sample(self) -> List[TelemetryEvent]:
        with self.sample_events_path.open("r", encoding="utf-8") as f:
            raw_events = json.load(f)
        return [TelemetryEvent(**event) for event in raw_events]

    def filter_events_for_event_hub(self, events: List[TelemetryEvent]) -> List[TelemetryEvent]:
        with self.filter_config_path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        filter_cfg = config.get("azure_event_hub", {}).get("filter", {})
        include_domains = set(filter_cfg.get("include_domains", []))
        include_entities = set(filter_cfg.get("include_entities", []))
        include_entity_globs = filter_cfg.get("include_entity_globs", [])
        exclude_domains = set(filter_cfg.get("exclude_domains", []))

        filtered: List[TelemetryEvent] = []
        for event in events:
            if event.domain in exclude_domains:
                continue

            include_match = False
            if event.domain in include_domains:
                include_match = True
            if event.entity_id in include_entities:
                include_match = True
            if any(fnmatch.fnmatch(event.entity_id, pattern) for pattern in include_entity_globs):
                include_match = True

            if include_match:
                filtered.append(event)

        return filtered

    def propose_automation_yaml(self, title: str, trigger: Dict[str, Any], condition: List[Dict[str, Any]], action: List[Dict[str, Any]]) -> str:
        automation = {
            "alias": title,
            "mode": "single",
            "trigger": [trigger],
            "condition": condition,
            "action": action,
        }
        return yaml.safe_dump(automation, sort_keys=False)

    def apply_automation_yaml(self, yaml_definition: str) -> Dict[str, str]:
        # Staged only for demo safety. No execution against Home Assistant in local mode.
        _ = yaml_definition
        return {
            "status": "staged",
            "message": "Automation YAML staged for review; no live Home Assistant execution performed.",
        }
