from __future__ import annotations

import json

from petbot.domain.brain.decision import BrainDecision, BrainRequest, MemoryCandidate
from petbot.domain.face.face_state import Expression
from petbot.domain.memory.memory import MemoryType
from petbot.interfaces.ai_provider import AIProvider


ALLOWED_ACTIONS = frozenset({"BLINK", "SET_EXPRESSION", "REMEMBER", "FORGET"})
FALLBACK_DECISION = BrainDecision("Perdona, necesito un momento para pensar.", Expression.CONFUSED)


class DecisionValidator:
    def validate(self, raw_decision: str) -> BrainDecision:
        try:
            data = json.loads(raw_decision)
        except json.JSONDecodeError as error:
            raise ValueError("La decisión de IA no contiene JSON válido.") from error
        speech = data.get("speech")
        if not isinstance(speech, str) or not speech.strip():
            raise ValueError("La decisión necesita una respuesta de texto.")
        try:
            expression = Expression(data.get("expression", Expression.NEUTRAL.value))
        except ValueError as error:
            raise ValueError("La expresión solicitada no existe.") from error
        actions = tuple(data.get("actions", []))
        if not all(isinstance(action, str) and action in ALLOWED_ACTIONS for action in actions):
            raise ValueError("La decisión contiene una acción no permitida.")
        candidates = tuple(
            MemoryCandidate(
                content=item["content"], type=MemoryType(item.get("type", MemoryType.SEMANTIC.value)),
                importance=float(item.get("importance", 0.6)), confidence=float(item.get("confidence", 0.8)),
            )
            for item in data.get("memory_candidates", [])
        )
        return BrainDecision(speech.strip(), expression, actions, candidates)


class BrainService:
    def __init__(self, provider: AIProvider, validator: DecisionValidator | None = None) -> None:
        self._provider = provider
        self._validator = validator or DecisionValidator()

    def converse(self, request: BrainRequest) -> BrainDecision:
        try:
            return self._validator.validate(self._provider.decide(request))
        except (TimeoutError, ConnectionError, ValueError):
            return FALLBACK_DECISION
