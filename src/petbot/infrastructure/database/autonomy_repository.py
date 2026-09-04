from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from petbot.infrastructure.database.sqlite import connect


@dataclass(frozen=True)
class StoredAutonomy:
    mode: str = "normal"
    is_sleeping: bool = False


class SQLiteAutonomyRepository:
    def __init__(self, database_path: Path) -> None:
        self._connection = connect(database_path)

    def get(self, pet_id: UUID) -> StoredAutonomy:
        row = self._connection.execute("SELECT mode, is_sleeping FROM pet_autonomy WHERE pet_id = ?", (str(pet_id),)).fetchone()
        return StoredAutonomy(row["mode"], bool(row["is_sleeping"])) if row else StoredAutonomy()

    def save(self, pet_id: UUID, state: StoredAutonomy) -> None:
        with self._connection:
            self._connection.execute(
                "INSERT INTO pet_autonomy (pet_id, mode, is_sleeping) VALUES (?, ?, ?) ON CONFLICT(pet_id) DO UPDATE SET mode = excluded.mode, is_sleeping = excluded.is_sleeping",
                (str(pet_id), state.mode, int(state.is_sleeping)),
            )
