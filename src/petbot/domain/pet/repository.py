from __future__ import annotations

from typing import Protocol
from uuid import UUID

from petbot.domain.pet.pet import Pet
from petbot.domain.personality.personality import Personality
from petbot.domain.personality.emotions import EmotionalState


class PetRepository(Protocol):
    def get_active(self) -> tuple[Pet, Personality] | None: ...

    def save(self, pet: Pet, personality: Personality) -> None: ...

    def get_by_id(self, pet_id: UUID) -> tuple[Pet, Personality] | None: ...

    def update_personality(self, pet_id: UUID, personality: Personality, *, cause: str) -> None: ...

    def load_emotional_state(self, pet_id: UUID) -> EmotionalState: ...

    def save_emotional_state(self, pet_id: UUID, state: EmotionalState) -> None: ...
