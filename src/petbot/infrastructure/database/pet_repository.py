from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from petbot.domain.personality.personality import Personality, PersonalityPreset
from petbot.domain.personality.traits import Trait
from petbot.domain.pet.identity import Identity
from petbot.domain.pet.pet import Pet
from petbot.infrastructure.database.sqlite import connect


class SQLitePetRepository:
    def __init__(self, database_path: Path) -> None:
        self._connection = connect(database_path)

    def get_active(self) -> tuple[Pet, Personality] | None:
        row = self._connection.execute("SELECT * FROM pets WHERE is_active = 1").fetchone()
        return self._to_aggregate(row) if row is not None else None

    def get_by_id(self, pet_id: UUID) -> tuple[Pet, Personality] | None:
        row = self._connection.execute("SELECT * FROM pets WHERE id = ?", (str(pet_id),)).fetchone()
        return self._to_aggregate(row) if row is not None else None

    def save(self, pet: Pet, personality: Personality) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        with self._connection:
            if pet.is_active:
                self._connection.execute("UPDATE pets SET is_active = 0 WHERE is_active = 1")
            self._connection.execute(
                "INSERT INTO pets (id, name, owner_name, created_at, is_active, schema_version) VALUES (?, ?, ?, ?, ?, ?)",
                (str(pet.id), pet.identity.name, pet.identity.owner_name, pet.created_at.isoformat(), int(pet.is_active), pet.schema_version),
            )
            self._connection.executemany(
                "INSERT INTO personality_traits (pet_id, trait, base_value, current_value, updated_at) VALUES (?, ?, ?, ?, ?)",
                [(str(pet.id), trait.value, value, value, timestamp) for trait, value in personality.values.items()],
            )

    def _to_aggregate(self, row: object) -> tuple[Pet, Personality]:
        pet = Pet(id=UUID(row["id"]), identity=Identity(row["name"], row["owner_name"]), created_at=datetime.fromisoformat(row["created_at"]), is_active=bool(row["is_active"]), schema_version=row["schema_version"])
        traits = self._connection.execute("SELECT trait, current_value FROM personality_traits WHERE pet_id = ?", (row["id"],)).fetchall()
        values = {Trait(item["trait"]): item["current_value"] for item in traits}
        return pet, Personality(preset=self._infer_preset(values), values=values)

    @staticmethod
    def _infer_preset(values: dict[Trait, int]) -> PersonalityPreset:
        # El preset es origen de los valores; por ahora se conserva mediante coincidencia.
        for preset in PersonalityPreset:
            if values == Personality.from_preset(preset).values:
                return preset
        return PersonalityPreset.BALANCED
