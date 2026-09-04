from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class EventType(str, Enum):
    PERSON_DETECTED = "PERSON_DETECTED"
    FACE_DETECTED = "FACE_DETECTED"
    OBJECT_DETECTED = "OBJECT_DETECTED"
    PERSON_ENTERED_VIEW = "PERSON_ENTERED_VIEW"
    PERSON_LEFT_VIEW = "PERSON_LEFT_VIEW"


@dataclass(frozen=True)
class PerceptionEvent:
    type: EventType
    source: str
    occurred_at: datetime

    @classmethod
    def create(cls, type: EventType, source: str = "camera") -> "PerceptionEvent":
        return cls(type, source, datetime.now(timezone.utc))
