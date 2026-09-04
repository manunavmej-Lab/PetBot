from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import UUID

from petbot.infrastructure.database.sqlite import connect


class SQLiteLifecycleRepository:
    def __init__(self, database_path: Path) -> None:
        self._connection = connect(database_path)

    def get_last_tick(self, pet_id: UUID) -> datetime | None:
        row = self._connection.execute("SELECT last_tick_at FROM pet_lifecycle WHERE pet_id = ?", (str(pet_id),)).fetchone()
        return datetime.fromisoformat(row["last_tick_at"]) if row is not None else None

    def save_last_tick(self, pet_id: UUID, moment: datetime) -> None:
        with self._connection:
            self._connection.execute(
                "INSERT INTO pet_lifecycle (pet_id, last_tick_at) VALUES (?, ?) ON CONFLICT(pet_id) DO UPDATE SET last_tick_at = excluded.last_tick_at",
                (str(pet_id), moment.isoformat()),
            )
