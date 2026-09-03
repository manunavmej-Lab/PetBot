from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Expression(str, Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    EXCITED = "excited"
    SAD = "sad"
    SLEEPY = "sleepy"
    SURPRISED = "surprised"
    CONFUSED = "confused"
    ANNOYED = "annoyed"


class Gaze(str, Enum):
    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"


class MouthState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    SMILE = "smile"
    FROWN = "frown"


@dataclass(frozen=True)
class FaceState:
    expression: Expression = Expression.NEUTRAL
    gaze: Gaze = Gaze.CENTER
    mouth: MouthState = MouthState.CLOSED
    eyes_closed: bool = False
    left_eye_closed: bool = False
    right_eye_closed: bool = False
    sleeping: bool = False

    def with_expression(self, expression: Expression) -> "FaceState":
        return FaceState(expression=expression, gaze=self.gaze, mouth=self.mouth, sleeping=expression is Expression.SLEEPY)
