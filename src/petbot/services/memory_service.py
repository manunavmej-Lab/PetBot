from __future__ import annotations

from datetime import datetime
from uuid import UUID

from petbot.domain.memory.memory import Memory, MemoryType
from petbot.domain.memory.repository import MemoryRepository


class MemoryService:
    def __init__(self, repository: MemoryRepository) -> None:
        self._repository = repository

    def remember(self, *, pet_id: UUID, type: MemoryType, content: str, importance: float, confidence: float, source: str, expires_at: datetime | None = None) -> Memory:
        duplicate = self._repository.find_duplicate(pet_id, type, content)
        if duplicate is not None:
            return duplicate
        memory = Memory.create(pet_id=pet_id, type=type, content=content, importance=importance, confidence=confidence, source=source, expires_at=expires_at)
        self._repository.save(memory)
        return memory

    def recall(self, pet_id: UUID, *, type: MemoryType | None = None) -> list[Memory]:
        return self._repository.list_for_pet(pet_id, type=type)

    def forget(self, pet_id: UUID, memory_id: UUID) -> bool:
        return self._repository.delete(memory_id, pet_id=pet_id)

    def consolidate(self) -> int:
        """Elimina recuerdos caducados; la consolidación semántica llegará con la búsqueda vectorial."""
        return self._repository.delete_expired()
