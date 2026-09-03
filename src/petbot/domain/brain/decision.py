from __future__ import annotations

from dataclasses import dataclass, field

from petbot.domain.face.face_state import Expression
from petbot.domain.memory.memory import MemoryType


@dataclass(frozen=True)
class BrainRequest:
    user_text: str
    pet_name: str
    owner_name: str
    personality_summary: str
    emotional_summary: str
    memories: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MemoryCandidate:
    content: str
    type: MemoryType = MemoryType.SEMANTIC
    importance: float = 0.6
    confidence: float = 0.8


@dataclass(frozen=True)
class BrainDecision:
    speech: str
    expression: Expression
    actions: tuple[str, ...] = ()
    memory_candidates: tuple[MemoryCandidate, ...] = ()
