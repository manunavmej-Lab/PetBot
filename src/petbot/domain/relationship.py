from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(frozen=True)
class KnownPerson:
    id: UUID
    pet_id: UUID
    name: str
    embedding: tuple[float, ...]
    consented_at: datetime

    @classmethod
    def create(cls, pet_id: UUID, name: str, embedding: list[float], consented_at: datetime) -> "KnownPerson":
        if not name.strip() or not embedding:
            raise ValueError("Se requieren nombre y huella facial para registrar una persona.")
        return cls(uuid4(), pet_id, name.strip(), tuple(embedding), consented_at)
