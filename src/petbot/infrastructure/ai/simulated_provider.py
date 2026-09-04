from __future__ import annotations

import json

from petbot.domain.brain.decision import BrainRequest


class SimulatedAIProvider:
    """Proveedor offline con reglas, útil para probar el contrato del cerebro."""

    def decide(self, request: BrainRequest) -> str:
        text = request.user_text.casefold()
        if any(word in text for word in ("triste", "mal", "cansado")):
            decision = {"speech": f"Lo siento, {request.owner_name}. Estoy contigo.", "expression": "sad", "actions": ["BLINK"]}
        elif any(word in text for word in ("hola", "buenas")):
            decision = {"speech": f"¡Hola, {request.owner_name}! Soy {request.pet_name}. Me gustaría jugar contigo.", "expression": "happy", "actions": ["BLINK"]}
        elif "sorpresa" in text or "guau" in text:
            decision = {"speech": "¡Vaya, eso sí que es sorprendente!", "expression": "surprised", "actions": ["BLINK"]}
        elif text.startswith("me gusta "):
            content = request.user_text.removeprefix("me gusta ").strip()
            decision = {"speech": f"Lo recordaré: te gusta {content}.", "expression": "happy", "actions": ["REMEMBER"], "memory_candidates": [{"content": f"A {request.owner_name} le gusta {content}", "importance": 0.7, "confidence": 0.9}]}
        else:
            decision = {"speech": f"Te escucho, {request.owner_name}. Cuéntame más.", "expression": "neutral", "actions": []}
        return json.dumps(decision)
