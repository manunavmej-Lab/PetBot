from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

from petbot.domain.relationship import KnownPerson
from petbot.infrastructure.database.sqlite import connect


class SQLitePeopleRepository:
    def __init__(self, database_path: Path) -> None:
        self._connection = connect(database_path)

    def save(self, person: KnownPerson) -> None:
        with self._connection:
            self._connection.execute("INSERT OR REPLACE INTO known_people (id, pet_id, display_name, face_embedding, consented_at) VALUES (?, ?, ?, ?, ?)", (str(person.id), str(person.pet_id), person.name, json.dumps(person.embedding), person.consented_at.isoformat()))

    def list_for_pet(self, pet_id: UUID) -> list[KnownPerson]:
        rows = self._connection.execute("SELECT * FROM known_people WHERE pet_id = ?", (str(pet_id),)).fetchall()
        return [KnownPerson(UUID(row["id"]), UUID(row["pet_id"]), row["display_name"], tuple(json.loads(row["face_embedding"])), datetime.fromisoformat(row["consented_at"])) for row in rows]
