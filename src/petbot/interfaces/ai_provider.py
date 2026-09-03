from __future__ import annotations

from typing import Protocol

from petbot.domain.brain.decision import BrainRequest


class AIProvider(Protocol):
    def decide(self, request: BrainRequest) -> str: ...
