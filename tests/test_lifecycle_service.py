from datetime import datetime, timedelta, timezone
from tempfile import TemporaryDirectory
from pathlib import Path

from petbot.domain.personality.emotions import Emotion
from petbot.domain.personality.personality import PersonalityPreset
from petbot.infrastructure.database.lifecycle_repository import SQLiteLifecycleRepository
from petbot.infrastructure.database.pet_repository import SQLitePetRepository
from petbot.services.lifecycle_service import LifecycleService
from petbot.services.personality_service import PersonalityService
from petbot.services.pet_service import PetService


def test_lifecycle_slowly_reduces_energy_after_time_passes() -> None:
    with TemporaryDirectory() as directory:
        database_path = Path(directory) / "petbot.db"
        pet_repository = SQLitePetRepository(database_path)
        session = PetService(pet_repository).create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED)
        service = LifecycleService(PersonalityService(pet_repository), SQLiteLifecycleRepository(database_path))
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)

        assert service.tick(session.pet.id, now=start) is None
        state = service.tick(session.pet.id, now=start + timedelta(minutes=30))

        assert state is not None
        assert state.values[Emotion.ENERGY] == 48
        assert state.values[Emotion.HAPPINESS] == 49
        assert state.values[Emotion.STRESS] == 1
