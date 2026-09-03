from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class MemoryType(str, Enum):
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    RELATIONAL = "relational"
    TEMPORARY = "temporary"
    VISUAL = "visual"


@dataclass(frozen=True)
class Memory:
    id: UUID
    pet_id: UUID
    type: MemoryType
    content: str
    importance: float
    confidence: float
    source: str
    created_at: datetime
    last_accessed_at: datetime
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("El contenido de un recuerdo no puede estar vacío.")
        if not self.source.strip():
            raise ValueError("El origen de un recuerdo no puede estar vacío.")
        if not 0 <= self.importance <= 1 or not 0 <= self.confidence <= 1:
            raise ValueError("La importancia y confianza deben estar entre 0 y 1.")

    @classmethod
    def create(cls, *, pet_id: UUID, type: MemoryType, content: str, importance: float, confidence: float, source: str, expires_at: datetime | None = None) -> "Memory":
        now = datetime.now(timezone.utc)
        return cls(uuid4(), pet_id, type, content.strip(), importance, confidence, source.strip(), now, now, expires_at)

    def is_expired(self, now: datetime | None = None) -> bool:
        return self.expires_at is not None and self.expires_at <= (now or datetime.now(timezone.utc))
