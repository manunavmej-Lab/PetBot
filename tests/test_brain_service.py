import json

from petbot.domain.brain.decision import BrainRequest
from petbot.domain.face.face_state import Expression
from petbot.infrastructure.ai.simulated_provider import SimulatedAIProvider
from petbot.services.brain_service import BrainService, DecisionValidator, FALLBACK_DECISION


def request(text: str = "hola") -> BrainRequest:
    return BrainRequest(text, "Buvi", "Manu", "alegría=75", "felicidad=50")


def test_simulated_brain_returns_valid_response() -> None:
    decision = BrainService(SimulatedAIProvider()).converse(request())

    assert "Hola" in decision.speech
    assert decision.expression is Expression.HAPPY


def test_validator_rejects_invalid_json_and_unknown_actions() -> None:
    validator = DecisionValidator()

    for raw in ("not-json", json.dumps({"speech": "hola", "expression": "happy", "actions": ["MOVE_NOW"]})):
        try:
            validator.validate(raw)
        except ValueError:
            pass
        else:
            raise AssertionError("La decisión debía ser inválida")


def test_provider_failure_timeout_and_missing_speech_use_fallback() -> None:
    class FailingProvider:
        def decide(self, request: BrainRequest) -> str:
            raise TimeoutError

    class EmptyProvider:
        def decide(self, request: BrainRequest) -> str:
            return '{"speech": "", "expression": "neutral"}'

    assert BrainService(FailingProvider()).converse(request()) == FALLBACK_DECISION
    assert BrainService(EmptyProvider()).converse(request()) == FALLBACK_DECISION


def test_simulated_brain_proposes_memory_candidate() -> None:
    decision = BrainService(SimulatedAIProvider()).converse(request("me gusta dormir al sol"))

    assert decision.memory_candidates[0].content == "A Manu le gusta dormir al sol"
