from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic
from typing import Callable

from petbot.domain.memory.memory import MemoryType
from petbot.domain.brain.decision import BrainRequest
from petbot.domain.face.face_state import Expression
from petbot.domain.events import EventType
from petbot.domain.personality.emotions import Emotion
from petbot.domain.personality.evolution import PersonalityChange
from petbot.domain.personality.traits import Trait
from petbot.services.memory_service import MemoryService
from petbot.services.brain_service import BrainService
from petbot.services.voice_service import VoiceService
from petbot.services.vision_service import VisionService
from petbot.services.people_service import PeopleService
from petbot.services.personality_service import PersonalityService
from petbot.services.pet_service import PetSession


@dataclass
class DevelopmentConsole:
    session: PetSession
    memory_service: MemoryService
    personality_service: PersonalityService
    input_fn: Callable[[str], str] = input
    output_fn: Callable[[str], None] = print
    on_play: Callable[[], None] = lambda: None
    on_expression: Callable[[Expression], None] = lambda expression: None
    on_blink: Callable[[], None] = lambda: None
    on_speech: Callable[[str], None] = lambda text: None
    brain_service: BrainService | None = None
    voice_service: VoiceService | None = None
    vision_service: VisionService | None = None
    vision_factory: Callable[[], VisionService] | None = None
    people_service: PeopleService | None = None
    on_person_entered: Callable[[], None] = lambda: None
    _pending_face_embedding: list[float] | None = None
    _pending_person_name: str | None = None
    _people_left_to_introduce: int = 0
    _recognized_people_count: int = 0
    _waiting_for_person_ready: bool = False
    _vision_unavailable: bool = False
    _camera_preview_visible: bool = False
    _last_greeting_at: dict[str, float] = field(default_factory=dict)

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
            self.output_fn("Comandos: ayuda, manual, hablar, ver, vista, estado, recuerda <texto>, recuerdos, jugar, salir")
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
        if normalized == "hablar":
            self._listen()
            return False
        if normalized == "ver":
            self._observe()
            return False
        if normalized == "vista":
            self._toggle_camera_preview()
            return False
        self._converse(normalized)
        return False

    def _remember(self, content: str) -> None:
        if not content.strip():
            self.output_fn("Indica qué quieres que recuerde.")
            return
        memory = self.memory_service.remember(
            pet_id=self.session.pet.id, type=MemoryType.SEMANTIC, content=content,
            importance=0.7, confidence=1.0, source="consola de desarrollo",
        )
        message = f"¡Pum! Ya lo guardé en mi memoria. Prometo no comérmelo."
        self.output_fn(f"Lo recordaré: {memory.content}. {message}")
        self.on_expression(Expression.HAPPY)
        self.on_blink()
        self.on_speech(message)

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
        self.on_play()
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
        self.output_fn("Comandos: hablar, ver, vista, estado, recuerda <texto>, recuerdos, jugar, salir.")

    def _toggle_camera_preview(self) -> None:
        if self.vision_service is None:
            if self.vision_factory is None:
                self.output_fn("La visión no está disponible.")
                return
            try:
                self.vision_service = self.vision_factory()
            except RuntimeError as error:
                self._vision_unavailable = True
                self.output_fn(f"No he podido activar la cámara: {error}")
                return
        if self.vision_service is None:
            self.output_fn("No he podido activar la cámara para mostrar su vista.")
            return
        enabled = not self._camera_preview_visible
        if not self.vision_service.set_preview_enabled(enabled):
            self.output_fn("Esta cámara no permite mostrar una vista de desarrollo.")
            return
        self._camera_preview_visible = enabled
        self.output_fn("Vista de cámara abierta." if enabled else "Vista de cámara cerrada.")

    def _observe(self, *, report: bool = True) -> None:
        if self._vision_unavailable:
            if report:
                self.output_fn("La visión no está disponible. Reinicia PETBOT después de revisar la cámara.")
            return
        if self.vision_service is None:
            if self.vision_factory is None:
                self.output_fn("La visión no está disponible.")
                return
            try:
                self.vision_service = self.vision_factory()
            except RuntimeError as error:
                self._vision_unavailable = True
                if report:
                    self.output_fn(f"No he podido activar la visión: {error}")
                return
        try:
            events = self.vision_service.observe_once()
        except RuntimeError as error:
            if report:
                self.output_fn(f"No he podido ver: {error}")
            return
        if report:
            self.output_fn("No detecto a nadie ahora." if not events else "Visión: " + ", ".join(event.type.value for event in events))
        if any(event.type is EventType.PERSON_ENTERED_VIEW for event in events):
            self._handle_person_entered()

    def observe_automatically(self) -> None:
        """Observa sin mensajes de depuración; solo reacciona ante una entrada."""
        self._observe(report=False)

    def close(self) -> None:
        if self.vision_service is not None:
            self.vision_service.close()

    def mobile_status(self) -> dict[str, object]:
        _, emotions = self.personality_service.get_state(self.session.pet.id)
        people = self.people_service.list_known_people(self.session.pet.id) if self.people_service else []
        return {
            "pet_name": self.session.pet.identity.name,
            "emotions": {emotion.value: value for emotion, value in emotions.values.items()},
            "known_people": [person.name for person in people],
        }

    def camera_image(self) -> bytes | None:
        return self.vision_service.latest_jpeg if self.vision_service else None

    def touch_status_lines(self) -> list[str]:
        _, emotions = self.personality_service.get_state(self.session.pet.id)
        return [
            f"Felicidad: {emotions.values[Emotion.HAPPINESS]}/100",
            f"Energía: {emotions.values[Emotion.ENERGY]}/100",
            f"Curiosidad: {emotions.values[Emotion.CURIOSITY]}/100",
            f"Afecto: {emotions.values[Emotion.AFFECTION]}/100",
        ]

    def touch_memory_lines(self) -> list[str]:
        memories = self.memory_service.recall(self.session.pet.id)[:5]
        return [memory.content for memory in memories] or ["Aún no tengo recuerdos guardados."]

    def rest_from_touch(self) -> None:
        self.personality_service.process_interaction(
            self.session.pet.id,
            emotional_changes={Emotion.ENERGY: 12, Emotion.STRESS: -10},
            personality_changes=[],
        )

    def wake_from_touch(self) -> None:
        self.personality_service.process_interaction(
            self.session.pet.id,
            emotional_changes={Emotion.ENERGY: 3, Emotion.HAPPINESS: 2},
            personality_changes=[],
        )

    def _handle_person_entered(self) -> None:
        if self._waiting_for_person_ready or self._pending_face_embedding is not None:
            return
        embeddings = self.vision_service.last_embeddings if self.vision_service else []
        if self.people_service is None or not embeddings:
            self.on_person_entered()
            return
        known_people = []
        unknown_embeddings = []
        for embedding in embeddings:
            person = self.people_service.identify(self.session.pet.id, embedding)
            if person is None:
                unknown_embeddings.append(embedding)
            elif person.name not in known_people:
                known_people.append(person.name)
        self._recognized_people_count = len(known_people)
        if not unknown_embeddings:
            people_to_greet = [name for name in known_people if self._can_greet(name)]
            if people_to_greet:
                greeting = _format_names(people_to_greet)
                self._respond_to_person(f"¡Hola, {greeting}! Me alegra veros otra vez. No queda nadie nuevo por presentar.", Expression.HAPPY)
            return
        people_to_greet = [name for name in known_people if self._can_greet(name)]
        if people_to_greet:
            greeting = _format_names(people_to_greet)
            self._respond_to_person(f"¡Hola, {greeting}! Me alegra veros otra vez.", Expression.HAPPY)
        self._people_left_to_introduce = len(unknown_embeddings)
        self._waiting_for_person_ready = True
        self._ask_for_next_person()

    def _listen(self) -> None:
        if self.voice_service is None:
            self.output_fn("La voz no está disponible.")
            return
        try:
            text = self.voice_service.listen()
        except (RuntimeError, TimeoutError) as error:
            self.output_fn(f"No he podido escucharte: {error}")
            return
        self.output_fn(f"Te he oído: {text}")
        self._converse(text)

    def _converse(self, text: str) -> None:
        if self._waiting_for_person_ready:
            self._capture_person_when_ready(text)
            return
        if self._pending_face_embedding is not None:
            self._continue_person_registration(text)
            return
        if self.brain_service is None:
            self.output_fn("No conozco ese comando. Escribe 'ayuda'.")
            return
        personality, emotions = self.personality_service.get_state(self.session.pet.id)
        memories = self.memory_service.recall(self.session.pet.id)
        request = BrainRequest(
            user_text=text, pet_name=self.session.pet.identity.name, owner_name=self.session.pet.identity.owner_name,
            personality_summary=", ".join(f"{trait.value}={value}" for trait, value in personality.values.items()),
            emotional_summary=", ".join(f"{emotion.value}={value}" for emotion, value in emotions.values.items()),
            memories=[memory.content for memory in memories[:5]],
        )
        decision = self.brain_service.converse(request)
        for candidate in decision.memory_candidates:
            self.memory_service.remember(pet_id=self.session.pet.id, type=candidate.type, content=candidate.content, importance=candidate.importance, confidence=candidate.confidence, source="cerebro simulado")
        self.on_expression(decision.expression)
        if "BLINK" in decision.actions:
            self.on_blink()
        self.output_fn(f"{self.session.pet.identity.name}: {decision.speech}")
        self.on_speech(decision.speech)

    def _continue_person_registration(self, text: str) -> None:
        if self._pending_person_name is None:
            name = _extract_name(text)
            if not name:
                self._respond_to_person("No he entendido el nombre. Dime, por ejemplo: me llamo Ana.", Expression.NEUTRAL)
                return
            self._pending_person_name = name
            self._respond_to_person(f"Encantado, {name}. ¿Quieres que recuerde tu cara en este Mac para reconocerte más adelante? Responde sí o no.", Expression.NEUTRAL)
            return
        if _is_affirmative(text) and self.people_service is not None:
            self.people_service.register_with_consent(self.session.pet.id, self._pending_person_name, self._pending_face_embedding)
            self._recognized_people_count += 1
            self._respond_to_person(f"Perfecto, {self._pending_person_name}. Guardaré una huella facial local para poder saludarte.", Expression.HAPPY)
        else:
            self._respond_to_person("De acuerdo. No guardaré tu cara.", Expression.NEUTRAL)
        self._pending_face_embedding = None
        self._pending_person_name = None
        self._people_left_to_introduce = max(0, self._people_left_to_introduce - 1)
        if self._people_left_to_introduce:
            self._waiting_for_person_ready = True
            self._ask_for_next_person()
        else:
            self._respond_to_person(f"Proceso terminado. He reconocido a {self._recognized_people_count} persona{_plural(self._recognized_people_count)} y no queda nadie pendiente.", Expression.HAPPY)

    def _ask_for_next_person(self) -> None:
        self._respond_to_person(
            f"He reconocido a {self._recognized_people_count} persona{_plural(self._recognized_people_count)}. {_remaining_verb(self._people_left_to_introduce)} {self._people_left_to_introduce} persona{_plural(self._people_left_to_introduce)} nueva{_plural(self._people_left_to_introduce, feminine=True)}. Ponte delante tú solo y dime 'listo' cuando estés preparado; entonces te preguntaré tu nombre.",
            Expression.SURPRISED,
        )

    def _capture_person_when_ready(self, text: str) -> None:
        if not _is_ready(text):
            self._respond_to_person("Cuando esté una sola persona delante de la cámara, dime 'listo'.", Expression.NEUTRAL)
            return
        if self.vision_service is None:
            self._respond_to_person("No tengo la cámara disponible para comprobarlo.", Expression.NEUTRAL)
            return
        try:
            self.vision_service.observe_once()
        except RuntimeError as error:
            self._respond_to_person(f"No he podido ver: {error}", Expression.NEUTRAL)
            return
        embeddings = self.vision_service.last_embeddings
        if len(embeddings) != 1:
            amount = len(embeddings)
            if amount == 0:
                self._respond_to_person("No veo a nadie todavía. Ponte delante tú solo y vuelve a decir 'listo'.", Expression.NEUTRAL)
            else:
                self._respond_to_person(f"Veo a {amount} personas. Para no confundir caras, debe quedar solo una delante y después decir 'listo'.", Expression.SURPRISED)
            return
        embedding = embeddings[0]
        if self.people_service is not None:
            known_person = self.people_service.identify(self.session.pet.id, embedding)
            if known_person is not None:
                self._respond_to_person(f"Ya reconozco a {known_person.name}. Deja delante a una persona nueva y vuelve a decir 'listo'.", Expression.HAPPY)
                return
        self._waiting_for_person_ready = False
        self._pending_face_embedding = embedding
        self._pending_person_name = None
        self._respond_to_person(f"Perfecto. Ahora solo veo a una persona. He reconocido a {self._recognized_people_count} y quedan {self._people_left_to_introduce} por presentar. ¿Cómo te llamas?", Expression.NEUTRAL)

    def _respond_to_person(self, message: str, expression: Expression) -> None:
        self.on_expression(expression)
        self.output_fn(f"{self.session.pet.identity.name}: {message}")
        self.on_speech(message)

    def _can_greet(self, name: str) -> bool:
        now = monotonic()
        last_greeting = self._last_greeting_at.get(name)
        if last_greeting is not None and now - last_greeting < 45:
            return False
        self._last_greeting_at[name] = now
        return True

    def process_spoken_text(self, text: str) -> None:
        self.output_fn(f"Te he oído: {text}")
        self._converse(text)


_LABELS = {
    "happiness": "felicidad", "energy": "energía", "curiosity": "curiosidad",
    "surprise": "sorpresa", "stress": "estrés", "affection": "afecto",
    "joy": "alegría", "sociability": "sociabilidad", "playfulness": "juego",
    "calmness": "calma", "courage": "valentía", "independence": "independencia",
}


def _extract_name(text: str) -> str:
    normalized = text.strip()
    lower = normalized.casefold()
    for prefix in ("me llamo ", "soy "):
        if lower.startswith(prefix):
            normalized = normalized[len(prefix):]
            break
    normalized = " ".join(part for part in normalized.split() if part.isalpha() or "-" in part)
    return normalized.title() if normalized else ""


def _is_affirmative(text: str) -> bool:
    return text.strip().casefold().strip(".!,¿?¡") in {"si", "sí", "claro", "vale", "de acuerdo", "por supuesto"}


def _is_ready(text: str) -> bool:
    return text.strip().casefold().strip(".!,¿?¡") in {"listo", "lista", "ya estoy", "preparado", "preparada"}


def _plural(amount: int, feminine: bool = False) -> str:
    if amount == 1:
        return ""
    return "s" if not feminine else "s"


def _remaining_verb(amount: int) -> str:
    return "Queda" if amount == 1 else "Quedan"


def _format_names(names: list[str]) -> str:
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} y {names[1]}"
    return f"{', '.join(names[:-1])} y {names[-1]}"
