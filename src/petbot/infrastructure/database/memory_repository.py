from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from petbot.domain.memory.memory import Memory, MemoryType
from petbot.infrastructure.database.sqlite import connect


class SQLiteMemoryRepository:
    def __init__(self, database_path: Path) -> None:
        self._connection = connect(database_path)

    def save(self, memory: Memory) -> None:
        with self._connection:
            self._connection.execute(
                "INSERT INTO memories (id, pet_id, type, content, normalized_content, importance, confidence, source, created_at, last_accessed_at, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (str(memory.id), str(memory.pet_id), memory.type.value, memory.content, _normalize(memory.content), memory.importance, memory.confidence, memory.source, memory.created_at.isoformat(), memory.last_accessed_at.isoformat(), memory.expires_at.isoformat() if memory.expires_at else None),
            )

    def get(self, memory_id: UUID) -> Memory | None:
        row = self._connection.execute("SELECT * FROM memories WHERE id = ?", (str(memory_id),)).fetchone()
        return self._to_memory(row) if row else None

    def list_for_pet(self, pet_id: UUID, *, type: MemoryType | None = None) -> list[Memory]:
        query = "SELECT * FROM memories WHERE pet_id = ? AND (expires_at IS NULL OR expires_at > ?)"
        values: list[str] = [str(pet_id), datetime.now(timezone.utc).isoformat()]
        if type is not None:
            query += " AND type = ?"
            values.append(type.value)
        query += " ORDER BY importance DESC, created_at DESC"
        memories = [self._to_memory(row) for row in self._connection.execute(query, values).fetchall()]
        self._touch(memories)
        return memories

    def find_duplicate(self, pet_id: UUID, type: MemoryType, content: str) -> Memory | None:
        row = self._connection.execute(
            "SELECT * FROM memories WHERE pet_id = ? AND type = ? AND normalized_content = ? AND (expires_at IS NULL OR expires_at > ?)",
            (str(pet_id), type.value, _normalize(content), datetime.now(timezone.utc).isoformat()),
        ).fetchone()
        return self._to_memory(row) if row else None

    def delete(self, memory_id: UUID, *, pet_id: UUID) -> bool:
        with self._connection:
            result = self._connection.execute("DELETE FROM memories WHERE id = ? AND pet_id = ?", (str(memory_id), str(pet_id)))
        return result.rowcount == 1

    def delete_expired(self) -> int:
        with self._connection:
            result = self._connection.execute("DELETE FROM memories WHERE expires_at IS NOT NULL AND expires_at <= ?", (datetime.now(timezone.utc).isoformat(),))
        return result.rowcount

    def _touch(self, memories: list[Memory]) -> None:
        if not memories:
            return
        now = datetime.now(timezone.utc).isoformat()
        with self._connection:
            self._connection.executemany("UPDATE memories SET last_accessed_at = ? WHERE id = ?", [(now, str(memory.id)) for memory in memories])

    @staticmethod
    def _to_memory(row: object) -> Memory:
        return Memory(UUID(row["id"]), UUID(row["pet_id"]), MemoryType(row["type"]), row["content"], row["importance"], row["confidence"], row["source"], datetime.fromisoformat(row["created_at"]), datetime.fromisoformat(row["last_accessed_at"]), datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None)


def _normalize(content: str) -> str:
    return " ".join(content.casefold().split())
