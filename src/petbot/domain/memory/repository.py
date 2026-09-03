from __future__ import annotations

from typing import Protocol
from uuid import UUID

from petbot.domain.memory.memory import Memory, MemoryType


class MemoryRepository(Protocol):
    def save(self, memory: Memory) -> None: ...

    def get(self, memory_id: UUID) -> Memory | None: ...

    def list_for_pet(self, pet_id: UUID, *, type: MemoryType | None = None) -> list[Memory]: ...

    def find_duplicate(self, pet_id: UUID, type: MemoryType, content: str) -> Memory | None: ...

    def delete(self, memory_id: UUID, *, pet_id: UUID) -> bool: ...

    def delete_expired(self) -> int: ...
