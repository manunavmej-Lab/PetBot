from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from petbot.domain.relationship import KnownPerson


class PeopleService:
    def __init__(self, repository: object) -> None:
        self._repository = repository

    def register_with_consent(self, pet_id: UUID, name: str, embedding: list[float]) -> KnownPerson:
        person = KnownPerson.create(pet_id, name, embedding, datetime.now(timezone.utc))
        self._repository.save(person)
        return person

    def list_known_people(self, pet_id: UUID) -> list[KnownPerson]:
        return self._repository.list_for_pet(pet_id)

    def identify(self, pet_id: UUID, embedding: list[float], threshold: float = 0.45) -> KnownPerson | None:
        import math
        if not embedding:
            return None
        for person in self._repository.list_for_pet(pet_id):
            numerator = sum(a * b for a, b in zip(embedding, person.embedding))
            denominator = math.sqrt(sum(a * a for a in embedding)) * math.sqrt(sum(b * b for b in person.embedding))
            if denominator == 0:
                continue
            score = numerator / denominator
            if score >= threshold:
                return person
        return None
