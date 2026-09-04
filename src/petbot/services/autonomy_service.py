from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from petbot.domain.face.face_state import Expression
from petbot.domain.personality.emotions import Emotion, EmotionalState
from petbot.infrastructure.database.autonomy_repository import StoredAutonomy


@dataclass(frozen=True)
class AutonomousDecision:
    mode: str
    sleeping: bool
    expression: Expression
    speech: str | None = None


class AutonomyService:
    """Convierte el estado emocional en conducta visible sin repetir avisos."""

    def __init__(self, repository: object) -> None:
        self._repository = repository

    def is_sleeping(self, pet_id: UUID) -> bool:
        return self._repository.get(pet_id).is_sleeping

    def evaluate(self, pet_id: UUID, emotions: EmotionalState) -> AutonomousDecision:
        previous = self._repository.get(pet_id)
        decision = self._decide(emotions, previous)
        self._repository.save(pet_id, StoredAutonomy(decision.mode, decision.sleeping))
        if decision.mode == previous.mode and decision.sleeping == previous.is_sleeping:
            return AutonomousDecision(decision.mode, decision.sleeping, decision.expression)
        return decision

    def put_to_sleep(self, pet_id: UUID) -> AutonomousDecision:
        decision = AutonomousDecision("sleeping", True, Expression.SLEEPY, "Voy a descansar un rato. Cuida mi sueño.")
        self._repository.save(pet_id, StoredAutonomy(decision.mode, decision.sleeping))
        return decision

    def wake_up(self, pet_id: UUID) -> AutonomousDecision:
        decision = AutonomousDecision("normal", False, Expression.HAPPY, "¡Ya estoy despierto! Me siento mucho mejor.")
        self._repository.save(pet_id, StoredAutonomy(decision.mode, decision.sleeping))
        return decision

    def _decide(self, emotions: EmotionalState, previous: StoredAutonomy) -> AutonomousDecision:
        energy = emotions.values[Emotion.ENERGY]
        happiness = emotions.values[Emotion.HAPPINESS]
        stress = emotions.values[Emotion.STRESS]
        if previous.is_sleeping:
            if energy >= 70:
                return AutonomousDecision("normal", False, Expression.HAPPY, "He descansado muy bien. ¡Ya estoy listo!")
            return AutonomousDecision("sleeping", True, Expression.SLEEPY)
        if energy <= 15:
            return AutonomousDecision("sleeping", True, Expression.SLEEPY, "Estoy muy cansado. Voy a dormir un poco.")
        if energy <= 30:
            return AutonomousDecision("tired", False, Expression.SLEEPY, "Estoy algo cansado. Un descanso me vendría bien.")
        if stress >= 40:
            return AutonomousDecision("stressed", False, Expression.SAD, "Necesito un momento tranquilo para sentirme mejor.")
        if happiness <= 45:
            return AutonomousDecision("bored", False, Expression.NEUTRAL, "Tengo curiosidad. ¿Jugamos un poco?")
        if happiness >= 75:
            return AutonomousDecision("happy", False, Expression.HAPPY)
        return AutonomousDecision("normal", False, Expression.NEUTRAL)
