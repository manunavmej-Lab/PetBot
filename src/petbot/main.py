from __future__ import annotations

import os
import select
import sys
from collections.abc import Callable
from queue import Empty, SimpleQueue
from pathlib import Path

from petbot.domain.personality.personality import PersonalityPreset
from petbot.domain.personality.emotions import Emotion
from petbot.domain.face.face_state import Expression
from petbot.infrastructure.database.pet_repository import SQLitePetRepository
from petbot.infrastructure.database.memory_repository import SQLiteMemoryRepository
from petbot.infrastructure.database.people_repository import SQLitePeopleRepository
from petbot.infrastructure.database.lifecycle_repository import SQLiteLifecycleRepository
from petbot.infrastructure.database.autonomy_repository import SQLiteAutonomyRepository
from petbot.infrastructure.ai.simulated_provider import SimulatedAIProvider
from petbot.infrastructure.voice.macos_voice import MacSpeaker, MacSpeechToText, MacTextToSpeech
from petbot.infrastructure.voice.linux_voice import LinuxSpeaker, LinuxSpeechToText, LinuxTextToSpeech, PiperSpeaker
from petbot.infrastructure.events.in_memory_event_bus import InMemoryEventBus
from petbot.infrastructure.vision.opencv_vision import OpenCVCamera, OpenCVVisionDetector
from petbot.infrastructure.mobile.local_dashboard import LocalMobileDashboard, MobileDashboardState
from petbot.interfaces.development_console import DevelopmentConsole
from petbot.infrastructure.face.desktop_face_display import DesktopFaceDisplay
from petbot.infrastructure.face.reactions import DesktopFaceReactions
from petbot.services.memory_service import MemoryService
from petbot.services.brain_service import BrainService
from petbot.services.voice_service import VoiceService
from petbot.services.wake_word_service import WakeWordService
from petbot.services.vision_service import VisionService
from petbot.services.people_service import PeopleService
from petbot.services.lifecycle_service import LifecycleService
from petbot.services.autonomy_service import AutonomyService, AutonomousDecision
from petbot.services.personality_service import PersonalityService
from petbot.services.pet_service import PetService


def main() -> None:
    database_path = Path(os.environ.get("PETBOT_DATABASE_PATH", "data/petbot.db"))
    if sys.platform != "darwin":
        os.environ.setdefault("PETBOT_AUDIO_DEVICE", "plughw:CARD=MAX98357A,DEV=0")
        os.environ.setdefault("PETBOT_VOICE", "mb/mb-es3")
        os.environ.setdefault("PETBOT_SPEECH_SPEED", "125")
    pet_repository = SQLitePetRepository(database_path)
    service = PetService(pet_repository)
    session = service.load_active()
    if session is None:
        print("PETBOT no tiene mascota creada.\n")
        name = input("¿Cómo quieres que se llame? ")
        owner_name = input("¿Cómo te llamas? ")
        preset = _ask_preset()
        session = service.create_active(name=name, owner_name=owner_name, preset=preset)
        print("\nMascota creada.")
    else:
        print("Cargando mascota...")
    print(f"Hola {session.pet.identity.owner_name}. Soy {session.pet.identity.name}.")
    face = DesktopFaceDisplay()
    reactions = DesktopFaceReactions(face)
    speech_to_text, voice, speaker = _create_voice_services()
    reactions.on_start()
    console = DevelopmentConsole(
        session=session,
        memory_service=MemoryService(SQLiteMemoryRepository(database_path)),
        personality_service=PersonalityService(pet_repository),
        on_play=reactions.on_play,
        on_expression=reactions.on_expression,
        on_blink=reactions.on_blink,
        on_speech=voice.speak,
        brain_service=BrainService(SimulatedAIProvider()),
        voice_service=voice,
        vision_factory=lambda: VisionService(OpenCVCamera(), OpenCVVisionDetector(), InMemoryEventBus()),
        people_service=PeopleService(SQLitePeopleRepository(database_path)),
        on_person_entered=lambda: _greet_new_person(reactions, voice),
    )

    spoken_messages: SimpleQueue[str] = SimpleQueue()
    mobile_actions: SimpleQueue[tuple[str, str]] = SimpleQueue()
    mobile_state = MobileDashboardState()
    mobile_state.update(console.mobile_status(), None)
    dashboard = LocalMobileDashboard(mobile_state, mobile_actions)
    dashboard.start()
    autonomy = AutonomyService(SQLiteAutonomyRepository(database_path))
    face.configure_touch_menu({
        "Jugar": lambda: console.handle("jugar"),
        "Estado": lambda: face.show_info("ESTADO DE BULVI", console.touch_status_lines()),
        "Recuerdos": lambda: face.show_info("RECUERDOS DE BULVI", console.touch_memory_lines()),
        "Dormir": lambda: _apply_autonomy_decision(_put_bulvi_to_sleep(console, autonomy), reactions, face, voice),
        "Despertar": lambda: _apply_autonomy_decision(_wake_bulvi(console, autonomy), reactions, face, voice),
        "QR móvil": lambda: face.show_mobile_qr(dashboard.url),
    }, sleeping_actions={"Despertar": lambda: _apply_autonomy_decision(_wake_bulvi(console, autonomy), reactions, face, voice)})
    listener = WakeWordService(speech_to_text, session.pet.identity.name, spoken_messages.put, speaker.is_speaking) if sys.platform == "darwin" else None
    if listener is not None:
        listener.start()
    if listener is not None:
        print(f"{session.pet.identity.name} escucha cuando dices su nombre. Escribe 'ayuda' para ver los comandos.\n")
    else:
        print(f"{session.pet.identity.name} está listo en la pantalla. La escucha por voz se activará al conectar un micrófono.\n")
    print(f"Móvil (misma Wi‑Fi): {dashboard.url}\n")
    lifecycle = LifecycleService(console.personality_service, SQLiteLifecycleRepository(database_path))
    _run_console_with_face(console, reactions, face, spoken_messages, mobile_actions, listener.stop if listener else lambda: None, dashboard.stop, mobile_state, lifecycle, autonomy, voice)
    face.run()


def _greet_new_person(reactions: DesktopFaceReactions, voice: VoiceService) -> None:
    reactions.on_expression(Expression.SURPRISED)
    voice.speak("Hola, soy Bulvi. No te reconozco todavía. ¿Cómo te llamas?")


def _put_bulvi_to_sleep(console: DevelopmentConsole, autonomy: AutonomyService) -> AutonomousDecision:
    console.rest_from_touch()
    return autonomy.put_to_sleep(console.session.pet.id)


def _wake_bulvi(console: DevelopmentConsole, autonomy: AutonomyService) -> AutonomousDecision:
    console.wake_from_touch()
    return autonomy.wake_up(console.session.pet.id)


def _apply_autonomy_decision(decision: AutonomousDecision, reactions: DesktopFaceReactions, face: DesktopFaceDisplay, voice: VoiceService) -> None:
    if decision.sleeping:
        face.sleep()
    else:
        face.wake()
        reactions.on_autonomous_expression(decision.expression)
    if decision.speech:
        voice.speak(decision.speech)


def _create_voice_services() -> tuple[object, VoiceService, object]:
    if sys.platform == "darwin":
        speaker = MacSpeaker()
        return MacSpeechToText(), VoiceService(MacSpeechToText(), MacTextToSpeech(), speaker), speaker
    speaker = PiperSpeaker() if os.environ.get("PETBOT_TTS_ENGINE") == "piper" else LinuxSpeaker()
    speech_to_text = LinuxSpeechToText()
    return speech_to_text, VoiceService(speech_to_text, LinuxTextToSpeech(), speaker), speaker


def _run_console_with_face(console: DevelopmentConsole, reactions: DesktopFaceReactions, face: DesktopFaceDisplay, spoken_messages: SimpleQueue[str], mobile_actions: SimpleQueue[tuple[str, str]], stop_listener: Callable[[], None], stop_dashboard: Callable[[], None], mobile_state: MobileDashboardState, lifecycle: LifecycleService, autonomy: AutonomyService, voice: VoiceService) -> None:
    """Lee la terminal sin bloquear el bucle gráfico de Tk en macOS."""
    terminal_available = True

    def prompt() -> None:
        print("PETBOT > ", end="", flush=True)

    def poll_terminal() -> None:
        nonlocal terminal_available
        try:
            while True:
                console.process_spoken_text(spoken_messages.get_nowait())
        except Empty:
            pass
        try:
            while True:
                action, text = mobile_actions.get_nowait()
                if action == "jugar":
                    console.handle("jugar")
                elif action == "decir":
                    console.process_spoken_text(text)
                elif action == "recuerda":
                    console.handle(f"recuerda {text}")
        except Empty:
            pass
        ready, _, _ = select.select([sys.stdin], [], [], 0) if terminal_available else ([], [], [])
        if ready:
            command = sys.stdin.readline()
            if not command:
                terminal_available = False
            elif console.handle(command):
                stop_listener()
                stop_dashboard()
                console.close()
                reactions.close()
                return
            prompt()
        face.schedule(50, poll_terminal)

    def poll_vision() -> None:
        console.observe_automatically()
        mobile_state.update(console.mobile_status(), console.camera_image())
        face.schedule(1_500, poll_vision)

    def poll_lifecycle() -> None:
        _, emotions = console.personality_service.get_state(console.session.pet.id)
        state = lifecycle.tick(console.session.pet.id, sleeping=autonomy.is_sleeping(console.session.pet.id)) or emotions
        _apply_autonomy_decision(autonomy.evaluate(console.session.pet.id, state), reactions, face, voice)
        face.schedule(60_000, poll_lifecycle)

    prompt()
    face.schedule(50, poll_terminal)
    face.schedule(750, poll_vision)
    face.schedule(1_000, poll_lifecycle)


def _ask_preset() -> PersonalityPreset:
    options = {"1": PersonalityPreset.CALM, "2": PersonalityPreset.BALANCED, "3": PersonalityPreset.PLAYFUL}
    print("\nPersonalidad inicial:\n1. Tranquilo\n2. Equilibrado\n3. Juguetón")
    while True:
        selected = input("\n> ").strip()
        if selected in options:
            return options[selected]
        print("Selecciona 1, 2 o 3.")


if __name__ == "__main__":
    main()
