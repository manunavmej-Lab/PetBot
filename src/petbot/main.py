from __future__ import annotations

import os
import select
import sys
from pathlib import Path

from petbot.domain.personality.personality import PersonalityPreset
from petbot.infrastructure.database.pet_repository import SQLitePetRepository
from petbot.infrastructure.database.memory_repository import SQLiteMemoryRepository
from petbot.infrastructure.ai.simulated_provider import SimulatedAIProvider
from petbot.interfaces.development_console import DevelopmentConsole
from petbot.infrastructure.face.desktop_face_display import DesktopFaceDisplay
from petbot.infrastructure.face.reactions import DesktopFaceReactions
from petbot.services.memory_service import MemoryService
from petbot.services.brain_service import BrainService
from petbot.services.personality_service import PersonalityService
from petbot.services.pet_service import PetService


def main() -> None:
    database_path = Path(os.environ.get("PETBOT_DATABASE_PATH", "data/petbot.db"))
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
    reactions.on_start()
    console = DevelopmentConsole(
        session=session,
        memory_service=MemoryService(SQLiteMemoryRepository(database_path)),
        personality_service=PersonalityService(pet_repository),
        on_play=reactions.on_play,
        on_expression=reactions.on_expression,
        on_blink=reactions.on_blink,
        brain_service=BrainService(SimulatedAIProvider()),
    )

    print("Escribe 'ayuda' para ver los comandos.\n")
    _run_console_with_face(console, reactions, face)
    face.run()


def _run_console_with_face(console: DevelopmentConsole, reactions: DesktopFaceReactions, face: DesktopFaceDisplay) -> None:
    """Lee la terminal sin bloquear el bucle gráfico de Tk en macOS."""
    def prompt() -> None:
        print("PETBOT > ", end="", flush=True)

    def poll_terminal() -> None:
        ready, _, _ = select.select([sys.stdin], [], [], 0)
        if ready:
            command = sys.stdin.readline()
            if not command or console.handle(command):
                reactions.close()
                return
            prompt()
        face.schedule(50, poll_terminal)

    prompt()
    face.schedule(50, poll_terminal)


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
