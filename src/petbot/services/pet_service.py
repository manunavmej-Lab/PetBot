from __future__ import annotations

from dataclasses import dataclass

from petbot.domain.personality.personality import Personality, PersonalityPreset
from petbot.domain.pet.pet import Pet
from petbot.domain.pet.repository import PetRepository


@dataclass(frozen=True)
class PetSession:
    pet: Pet
    personality: Personality
    created: bool


class PetService:
    def __init__(self, repository: PetRepository) -> None:
        self._repository = repository

    def load_active(self) -> PetSession | None:
        stored = self._repository.get_active()
        if stored is None:
            return None
        pet, personality = stored
        return PetSession(pet=pet, personality=personality, created=False)

    def create_active(self, *, name: str, owner_name: str, preset: PersonalityPreset | str) -> PetSession:
        current = self.load_active()
        if current is not None:
            return current
        pet = Pet.create(name=name, owner_name=owner_name)
        personality = Personality.from_preset(preset)
        self._repository.save(pet, personality)
        return PetSession(pet=pet, personality=personality, created=True)
