from __future__ import annotations

import json
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from src.models.serialization import model_to_dict
from src.models.telemetry import EventHubEnvelope, TelemetryEvent


class AzureEventHubConnector:
    """Local Event Hub simulator for publish/consume behavior.

    TODO: Replace with azure-eventhub SDK using EventHubProducerClient/EventData.
    """

    def __init__(self, envelope_store_path: Path) -> None:
        self.envelope_store_path = envelope_store_path
        self.envelope_store_path.parent.mkdir(parents=True, exist_ok=True)

    def publish_event(self, event: TelemetryEvent) -> EventHubEnvelope:
        envelope = EventHubEnvelope(
            event_id=str(uuid.uuid4()),
            enqueued_time=datetime.utcnow(),
            partition_key=event.domain,
            source=event.source,
            payload=event,
        )
        self._append_envelope(envelope)
        return envelope

    def publish_batch(self, events: List[TelemetryEvent]) -> List[EventHubEnvelope]:
        return [self.publish_event(event) for event in events]

    def consume_events(self) -> List[EventHubEnvelope]:
        if not self.envelope_store_path.exists():
            return []

        with self.envelope_store_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)

        envelopes: List[EventHubEnvelope] = []
        for item in raw:
            payload = item["payload"]
            envelope = EventHubEnvelope(
                event_id=item["event_id"],
                enqueued_time=item.get("enqueued_time"),
                partition_key=item.get("partition_key"),
                source=item.get("source", "home_assistant"),
                payload=TelemetryEvent(**payload),
            )
            envelopes.append(envelope)
        return envelopes

    def get_ingestion_summary(self) -> Dict[str, object]:
        envelopes = self.consume_events()
        domains = Counter(envelope.payload.domain for envelope in envelopes)
        entities = Counter(envelope.payload.entity_id for envelope in envelopes)

        return {
            "total_published": len(envelopes),
            "domains": dict(domains),
            "top_entities": dict(entities.most_common(5)),
        }

    def _append_envelope(self, envelope: EventHubEnvelope) -> None:
        if self.envelope_store_path.exists():
            with self.envelope_store_path.open("r", encoding="utf-8") as f:
                current = json.load(f)
        else:
            current = []

        payload = model_to_dict(envelope)
        current.append(payload)

        with self.envelope_store_path.open("w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, default=str)
