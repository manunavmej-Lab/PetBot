from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from petbot.domain.personality.emotions import Emotion, EmotionalState
from petbot.services.personality_service import PersonalityService


class LifecycleService:
    """Evoluciona necesidades de forma lenta, persistente y sin cambios bruscos."""

    TICK_INTERVAL = timedelta(minutes=15)
    MAX_INTERVALS_PER_RUN = 8

    def __init__(self, personality_service: PersonalityService, repository: object) -> None:
        self._personality_service = personality_service
        self._repository = repository

    def tick(self, pet_id: UUID, *, sleeping: bool = False, now: datetime | None = None) -> EmotionalState | None:
        moment = now or datetime.now(timezone.utc)
        last_tick = self._repository.get_last_tick(pet_id)
        if last_tick is None or moment <= last_tick:
            self._repository.save_last_tick(pet_id, moment)
            return None
        intervals = min(int((moment - last_tick) // self.TICK_INTERVAL), self.MAX_INTERVALS_PER_RUN)
        if intervals == 0:
            return None
        changes = {Emotion.ENERGY: intervals * 4} if sleeping else {Emotion.ENERGY: -intervals}
        if not sleeping and intervals >= 2:
            changes[Emotion.HAPPINESS] = -1
            changes[Emotion.STRESS] = 1
        elif sleeping:
            changes[Emotion.STRESS] = -min(2, intervals)
        _, state = self._personality_service.process_interaction(pet_id, emotional_changes=changes, personality_changes=[])
        self._repository.save_last_tick(pet_id, last_tick + self.TICK_INTERVAL * intervals)
        return state
