from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from petbot.domain.personality.personality import Personality
from petbot.domain.personality.traits import Trait, TraitValue


MAX_CHANGE_PER_INTERACTION = 2


@dataclass(frozen=True)
class PersonalityChange:
    trait: Trait
    delta: int
    cause: str

    def __post_init__(self) -> None:
        if not self.cause.strip():
            raise ValueError("Cada cambio de personalidad necesita una causa.")
        if abs(self.delta) > MAX_CHANGE_PER_INTERACTION:
            raise ValueError(f"El cambio máximo por interacción es {MAX_CHANGE_PER_INTERACTION}.")


class EvolutionEngine:
    """Único componente de dominio autorizado a modificar la personalidad."""

    def evolve(self, personality: Personality, changes: list[PersonalityChange]) -> Personality:
        evolved = dict(personality.traits)
        for change in changes:
            current = evolved[change.trait]
            evolved[change.trait] = current.with_current(current.current_value + change.delta)
        return Personality(preset=personality.preset, traits=evolved)
