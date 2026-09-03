from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class Emotion(str, Enum):
    HAPPINESS = "happiness"
    ENERGY = "energy"
    CURIOSITY = "curiosity"
    SURPRISE = "surprise"
    STRESS = "stress"
    AFFECTION = "affection"


BASELINE: dict[Emotion, int] = {
    Emotion.HAPPINESS: 50, Emotion.ENERGY: 50, Emotion.CURIOSITY: 50,
    Emotion.SURPRISE: 0, Emotion.STRESS: 0, Emotion.AFFECTION: 50,
}


@dataclass(frozen=True)
class EmotionalState:
    values: Mapping[Emotion, int]

    @classmethod
    def neutral(cls) -> "EmotionalState":
        return cls(values=BASELINE.copy())

    def adjust(self, changes: Mapping[Emotion, int]) -> "EmotionalState":
        return EmotionalState({emotion: _bounded(self.values[emotion] + changes.get(emotion, 0)) for emotion in Emotion})

    def decay(self, amount: int = 1) -> "EmotionalState":
        if amount < 0:
            raise ValueError("El decaimiento debe ser positivo.")
        return EmotionalState({
            emotion: _towards(self.values[emotion], BASELINE[emotion], amount) for emotion in Emotion
        })


def _bounded(value: int) -> int:
    return max(0, min(100, value))


def _towards(value: int, target: int, amount: int) -> int:
    return max(target, value - amount) if value > target else min(target, value + amount)
