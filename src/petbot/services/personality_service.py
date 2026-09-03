from __future__ import annotations

from typing import Mapping
from uuid import UUID

from petbot.domain.personality.emotions import Emotion, EmotionalState
from petbot.domain.personality.evolution import EvolutionEngine, PersonalityChange
from petbot.domain.personality.personality import Personality
from petbot.domain.pet.repository import PetRepository


class PersonalityService:
    def __init__(self, repository: PetRepository, evolution_engine: EvolutionEngine | None = None) -> None:
        self._repository = repository
        self._evolution_engine = evolution_engine or EvolutionEngine()

    def process_interaction(self, pet_id: UUID, *, emotional_changes: Mapping[Emotion, int], personality_changes: list[PersonalityChange]) -> tuple[Personality, EmotionalState]:
        stored = self._repository.get_by_id(pet_id)
        if stored is None:
            raise ValueError("La mascota no existe.")
        _, personality = stored
        state = self._repository.load_emotional_state(pet_id).adjust(emotional_changes)
        evolved = self._evolution_engine.evolve(personality, personality_changes)
        cause = "; ".join(change.cause for change in personality_changes) or "interacción sin cambio de personalidad"
        self._repository.update_personality(pet_id, evolved, cause=cause)
        self._repository.save_emotional_state(pet_id, state)
        return evolved, state

    def decay_emotions(self, pet_id: UUID, amount: int = 1) -> EmotionalState:
        state = self._repository.load_emotional_state(pet_id).decay(amount)
        self._repository.save_emotional_state(pet_id, state)
        return state
