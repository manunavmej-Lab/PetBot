from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile

import pytest

from petbot.domain.memory.memory import MemoryType
from petbot.domain.personality.personality import Personality, PersonalityPreset
from petbot.domain.pet.pet import Pet
from petbot.infrastructure.database.memory_repository import SQLiteMemoryRepository
from petbot.infrastructure.database.pet_repository import SQLitePetRepository
from petbot.services.memory_service import MemoryService
from petbot.services.pet_service import PetService


@pytest.fixture
def memory_context() -> tuple[Path, PetService, MemoryService]:
    with tempfile.TemporaryDirectory() as temporary_directory:
        database_path = Path(temporary_directory) / "petbot.db"
        pet_repository = SQLitePetRepository(database_path)
        yield database_path, PetService(pet_repository), MemoryService(SQLiteMemoryRepository(database_path))


def test_remember_and_recall_after_repository_restart(memory_context: tuple[Path, PetService, MemoryService]) -> None:
    database_path, pet_service, memory_service = memory_context
    pet = pet_service.create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED).pet
    memory_service.remember(pet_id=pet.id, type=MemoryType.SEMANTIC, content="Manuel prefiere el color azul", importance=0.8, confidence=0.9, source="usuario")

    recalled = MemoryService(SQLiteMemoryRepository(database_path)).recall(pet.id)

    assert [memory.content for memory in recalled] == ["Manuel prefiere el color azul"]


def test_forget_removes_only_requested_memory(memory_context: tuple[Path, PetService, MemoryService]) -> None:
    _, pet_service, memory_service = memory_context
    pet = pet_service.create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED).pet
    memory = memory_service.remember(pet_id=pet.id, type=MemoryType.EPISODIC, content="Jugamos esta tarde", importance=0.5, confidence=0.8, source="simulación")

    assert memory_service.forget(pet.id, memory.id)
    assert memory_service.recall(pet.id) == []


def test_expired_memory_is_not_recalled_and_is_consolidated(memory_context: tuple[Path, PetService, MemoryService]) -> None:
    _, pet_service, memory_service = memory_context
    pet = pet_service.create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED).pet
    memory_service.remember(pet_id=pet.id, type=MemoryType.TEMPORARY, content="La puerta está abierta", importance=0.3, confidence=0.9, source="sensor", expires_at=datetime.now(timezone.utc) - timedelta(seconds=1))

    assert memory_service.recall(pet.id) == []
    assert memory_service.consolidate() == 1


def test_memories_are_isolated_between_pets(memory_context: tuple[Path, PetService, MemoryService]) -> None:
    database_path, pet_service, memory_service = memory_context
    first_pet = pet_service.create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED).pet
    second_pet = Pet.create(name="Luna", owner_name="Ana")
    SQLitePetRepository(database_path).save(second_pet, Personality.from_preset(PersonalityPreset.CALM))
    memory_service.remember(pet_id=first_pet.id, type=MemoryType.RELATIONAL, content="Manuel es mi propietario", importance=1.0, confidence=1.0, source="creación")

    assert memory_service.recall(second_pet.id) == []


def test_duplicate_memory_is_not_saved_twice(memory_context: tuple[Path, PetService, MemoryService]) -> None:
    _, pet_service, memory_service = memory_context
    pet = pet_service.create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED).pet
    first = memory_service.remember(pet_id=pet.id, type=MemoryType.SEMANTIC, content="Manuel vive en Madrid", importance=0.7, confidence=0.8, source="usuario")
    second = memory_service.remember(pet_id=pet.id, type=MemoryType.SEMANTIC, content=" manuel  vive en madrid ", importance=0.9, confidence=0.9, source="usuario")

    assert second.id == first.id
    assert len(memory_service.recall(pet.id)) == 1
