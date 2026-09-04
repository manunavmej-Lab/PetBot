from uuid import uuid4

from petbot.domain.personality.emotions import Emotion, EmotionalState
from petbot.infrastructure.database.autonomy_repository import StoredAutonomy
from petbot.services.autonomy_service import AutonomyService


class FakeAutonomyRepository:
    def __init__(self) -> None:
        self.state = StoredAutonomy()

    def get(self, pet_id: object) -> StoredAutonomy:
        return self.state

    def save(self, pet_id: object, state: StoredAutonomy) -> None:
        self.state = state


def test_autonomy_sleeps_when_energy_is_low_and_does_not_repeat_speech() -> None:
    service = AutonomyService(FakeAutonomyRepository())
    emotions = EmotionalState.neutral().adjust({Emotion.ENERGY: -40})

    first = service.evaluate(uuid4(), emotions)
    second = service.evaluate(uuid4(), emotions)

    assert first.sleeping
    assert first.speech is not None
    assert second.sleeping
    assert second.speech is None
