from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from petbot.domain.pet.identity import Identity


@dataclass(frozen=True)
class Pet:
    id: UUID
    identity: Identity
    created_at: datetime
    is_active: bool = True
    schema_version: int = 1

    @classmethod
    def create(cls, *, name: str, owner_name: str) -> "Pet":
        return cls(
            id=uuid4(),
            identity=Identity(name=name.strip(), owner_name=owner_name.strip()),
            created_at=datetime.now(timezone.utc),
        )
