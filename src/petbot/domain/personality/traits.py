from __future__ import annotations

from enum import Enum
from dataclasses import dataclass


class Trait(str, Enum):
    JOY = "joy"
    CURIOSITY = "curiosity"
    SOCIABILITY = "sociability"
    AFFECTION = "affection"
    PLAYFULNESS = "playfulness"
    CALMNESS = "calmness"
    COURAGE = "courage"
    INDEPENDENCE = "independence"


@dataclass(frozen=True)
class TraitValue:
    base_value: int
    current_value: int
    min_value: int = 0
    max_value: int = 100

    def __post_init__(self) -> None:
        if not 0 <= self.min_value <= self.max_value <= 100:
            raise ValueError("Los límites de un rasgo deben estar entre 0 y 100.")
        if not self.min_value <= self.base_value <= self.max_value:
            raise ValueError("El valor base está fuera de límites.")
        if not self.min_value <= self.current_value <= self.max_value:
            raise ValueError("El valor actual está fuera de límites.")

    def with_current(self, value: int) -> "TraitValue":
        return TraitValue(self.base_value, max(self.min_value, min(self.max_value, value)), self.min_value, self.max_value)
