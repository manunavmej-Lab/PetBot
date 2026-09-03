from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from petbot.domain.memory.memory import MemoryType
from petbot.domain.personality.emotions import Emotion
from petbot.domain.personality.evolution import PersonalityChange
from petbot.domain.personality.traits import Trait
from petbot.services.memory_service import MemoryService
from petbot.services.personality_service import PersonalityService
from petbot.services.pet_service import PetSession


@dataclass
class DevelopmentConsole:
    session: PetSession
    memory_service: MemoryService
    personality_service: PersonalityService
    input_fn: Callable[[str], str] = input
    output_fn: Callable[[str], None] = print

    def run(self) -> None:
        self.output_fn("Escribe 'ayuda' para ver los comandos.\n")
        while True:
            command = self.input_fn("PETBOT > ").strip()
            if self.handle(command):
                return

    def handle(self, command: str) -> bool:
        normalized = command.strip()
        if normalized in {"salir", "exit", "quit"}:
            self.output_fn("Hasta pronto.")
            return True
        if normalized in {"ayuda", "help"}:
            self.output_fn("Comandos: ayuda, manual, estado, recuerda <texto>, recuerdos, jugar, salir")
            return False
        if normalized == "manual":
            self._show_manual()
            return False
        if normalized == "estado":
            self._show_state()
            return False
        if normalized == "recuerdos":
            self._show_memories()
            return False
        if normalized.startswith("recuerda "):
            self._remember(normalized.removeprefix("recuerda "))
            return False
        if normalized == "jugar":
            self._play()
            return False
        self.output_fn("No conozco ese comando. Escribe 'ayuda'.")
        return False

    def _remember(self, content: str) -> None:
        if not content.strip():
            self.output_fn("Indica qué quieres que recuerde.")
            return
        memory = self.memory_service.remember(
            pet_id=self.session.pet.id, type=MemoryType.SEMANTIC, content=content,
            importance=0.7, confidence=1.0, source="consola de desarrollo",
        )
        self.output_fn(f"Lo recordaré: {memory.content}")

    def _show_memories(self) -> None:
        memories = self.memory_service.recall(self.session.pet.id)
        if not memories:
            self.output_fn("Aún no tengo recuerdos.")
            return
        self.output_fn("Recuerdos:")
        for memory in memories:
            self.output_fn(f"- {memory.content}")

    def _play(self) -> None:
        personality, emotions = self.personality_service.process_interaction(
            self.session.pet.id,
            emotional_changes={Emotion.HAPPINESS: 8, Emotion.ENERGY: 8},
            personality_changes=[PersonalityChange(Trait.PLAYFULNESS, 1, "jugó con su propietario")],
        )
        self.output_fn(f"¡Qué divertido! Alegría: {emotions.values[Emotion.HAPPINESS]}; juego: {personality.values[Trait.PLAYFULNESS]}.")

    def _show_state(self) -> None:
        current_personality, emotions = self.personality_service.get_state(self.session.pet.id)
        self.output_fn(f"Estado de {self.session.pet.identity.name}:")
        self.output_fn("Emociones:")
        for emotion in Emotion:
            self.output_fn(f"- {_LABELS[emotion.value]}: {emotions.values[emotion]}/100")
        self.output_fn("Personalidad:")
        for trait in Trait:
            value = current_personality.traits[trait]
            self.output_fn(f"- {_LABELS[trait.value]}: {value.current_value}/100 (base: {value.base_value})")

    def _show_manual(self) -> None:
        self.output_fn("Manual de PETBOT")
        self.output_fn("Emociones: cambian rápido con una interacción y vuelven gradualmente a su estado normal.")
        self.output_fn("Ejemplos: jugar aumenta felicidad y energía; un evento futuro podría aumentar estrés o sorpresa.")
        self.output_fn("Personalidad: cambia lentamente y describe el carácter estable de PETBOT.")
        self.output_fn("Cada interacción solo puede cambiar un rasgo un máximo de 2 puntos, siempre entre 0 y 100.")
        self.output_fn("Ejemplos: jugar aumenta el rasgo juego en 1 punto; las experiencias repetidas podrían influir en calma o curiosidad.")
        self.output_fn("Prueba: 'jugar', después 'estado'. Usa 'recuerda me gusta el azul' y 'recuerdos' para probar memoria.")
        self.output_fn("Comandos: estado, recuerda <texto>, recuerdos, jugar, salir.")


_LABELS = {
    "happiness": "felicidad", "energy": "energía", "curiosity": "curiosidad",
    "surprise": "sorpresa", "stress": "estrés", "affection": "afecto",
    "joy": "alegría", "sociability": "sociabilidad", "playfulness": "juego",
    "calmness": "calma", "courage": "valentía", "independence": "independencia",
}
