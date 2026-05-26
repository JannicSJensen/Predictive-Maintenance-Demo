from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

try:
    from pydantic import BaseModel, Field

    PYDANTIC_AVAILABLE = True
except ImportError:  # pragma: no cover
    from dataclasses import dataclass, field

    PYDANTIC_AVAILABLE = False


if PYDANTIC_AVAILABLE:

    class TelemetryEvent(BaseModel):
        timestamp: datetime
        entity_id: str
        domain: str
        state: str
        attributes: Dict[str, Any] = Field(default_factory=dict)
        room: Optional[str] = None
        source: str = "home_assistant"
        ingestion_path: str = "azure_event_hub"

    class EventHubEnvelope(BaseModel):
        event_id: str
        enqueued_time: Optional[datetime] = None
        partition_key: Optional[str] = None
        source: str = "home_assistant"
        payload: TelemetryEvent

else:

    @dataclass
    class TelemetryEvent:
        timestamp: datetime
        entity_id: str
        domain: str
        state: str
        attributes: Dict[str, Any] = field(default_factory=dict)
        room: Optional[str] = None
        source: str = "home_assistant"
        ingestion_path: str = "azure_event_hub"

    @dataclass
    class EventHubEnvelope:
        event_id: str
        enqueued_time: Optional[datetime] = None
        partition_key: Optional[str] = None
        source: str = "home_assistant"
        payload: TelemetryEvent = field(default_factory=TelemetryEvent)
