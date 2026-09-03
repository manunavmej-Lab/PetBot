from __future__ import annotations

import tempfile
from pathlib import Path

from petbot.domain.personality.personality import PersonalityPreset
from petbot.infrastructure.database.memory_repository import SQLiteMemoryRepository
from petbot.infrastructure.database.pet_repository import SQLitePetRepository
from petbot.interfaces.development_console import DevelopmentConsole
from petbot.services.memory_service import MemoryService
from petbot.services.personality_service import PersonalityService
from petbot.services.pet_service import PetService


def test_console_remembers_lists_and_plays() -> None:
    with tempfile.TemporaryDirectory() as directory:
        database_path = Path(directory) / "petbot.db"
        pet_repository = SQLitePetRepository(database_path)
        session = PetService(pet_repository).create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED)
        output: list[str] = []
        console = DevelopmentConsole(
            session=session,
            memory_service=MemoryService(SQLiteMemoryRepository(database_path)),
            personality_service=PersonalityService(pet_repository),
            output_fn=output.append,
        )

        console.handle("recuerda que me gusta el azul")
        console.handle("recuerdos")
        console.handle("jugar")
        console.handle("estado")

        assert "Lo recordaré: que me gusta el azul" in output
        assert "- que me gusta el azul" in output
        assert any("Qué divertido" in line for line in output)
        assert "Estado de Boti:" in output
        assert "Emociones:" in output
        assert "Personalidad:" in output


def test_console_exits_on_salir() -> None:
    with tempfile.TemporaryDirectory() as directory:
        database_path = Path(directory) / "petbot.db"
        pet_repository = SQLitePetRepository(database_path)
        session = PetService(pet_repository).create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED)
        output: list[str] = []
        console = DevelopmentConsole(session, MemoryService(SQLiteMemoryRepository(database_path)), PersonalityService(pet_repository), output_fn=output.append)

        assert console.handle("salir")
        assert output == ["Hasta pronto."]


def test_console_manual_explains_emotions_and_personality() -> None:
    with tempfile.TemporaryDirectory() as directory:
        database_path = Path(directory) / "petbot.db"
        pet_repository = SQLitePetRepository(database_path)
        session = PetService(pet_repository).create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED)
        output: list[str] = []
        console = DevelopmentConsole(session, MemoryService(SQLiteMemoryRepository(database_path)), PersonalityService(pet_repository), output_fn=output.append)

        assert not console.handle("manual")
        assert "Manual de PETBOT" in output
        assert any(line.startswith("Emociones:") for line in output)
        assert any(line.startswith("Personalidad:") for line in output)
