from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from petbot.domain.personality.personality import PersonalityPreset
from petbot.infrastructure.database.pet_repository import SQLitePetRepository
from petbot.services.pet_service import PetService


class PetLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        database_path = Path(self._temporary_directory.name) / "petbot.db"
        self.repository = SQLitePetRepository(database_path)
        self.service = PetService(self.repository)

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def test_creates_pet_when_none_exists(self) -> None:
        session = self.service.create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED)

        self.assertTrue(session.created)
        self.assertEqual("Boti", session.pet.identity.name)

    def test_loads_existing_pet(self) -> None:
        self.service.create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.CALM)

        session = self.service.load_active()

        self.assertIsNotNone(session)
        assert session is not None
        self.assertFalse(session.created)
        self.assertEqual("Manuel", session.pet.identity.owner_name)

    def test_second_creation_does_not_duplicate_active_pet(self) -> None:
        first = self.service.create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED)
        second = self.service.create_active(name="Otra", owner_name="Ana", preset=PersonalityPreset.PLAYFUL)

        self.assertEqual(first.pet.id, second.pet.id)
        self.assertFalse(second.created)

    def test_persists_personality(self) -> None:
        self.service.create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED)

        session = self.service.load_active()

        assert session is not None
        self.assertEqual(PersonalityPreset.BALANCED, session.personality.preset)
        self.assertEqual(85, session.personality.values[next(trait for trait in session.personality.values if trait.value == "curiosity")])

    def test_invalid_preset_raises_controlled_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "Preset de personalidad no válido"):
            self.service.create_active(name="Boti", owner_name="Manuel", preset="invalido")


if __name__ == "__main__":
    unittest.main()
