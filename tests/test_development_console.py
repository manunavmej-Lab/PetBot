from __future__ import annotations

import tempfile
from pathlib import Path

from petbot.domain.personality.personality import PersonalityPreset
from petbot.domain.personality.emotions import Emotion
from petbot.infrastructure.database.memory_repository import SQLiteMemoryRepository
from petbot.infrastructure.database.pet_repository import SQLitePetRepository
from petbot.infrastructure.database.people_repository import SQLitePeopleRepository
from petbot.interfaces.development_console import DevelopmentConsole
from petbot.services.memory_service import MemoryService
from petbot.services.people_service import PeopleService
from petbot.services.personality_service import PersonalityService
from petbot.services.pet_service import PetService


def test_console_remembers_lists_and_plays() -> None:
    with tempfile.TemporaryDirectory() as directory:
        database_path = Path(directory) / "petbot.db"
        pet_repository = SQLitePetRepository(database_path)
        session = PetService(pet_repository).create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED)
        output: list[str] = []
        reactions: list[str] = []
        console = DevelopmentConsole(
            session=session,
            memory_service=MemoryService(SQLiteMemoryRepository(database_path)),
            personality_service=PersonalityService(pet_repository),
            output_fn=output.append,
            on_play=lambda: reactions.append("play"),
        )

        console.handle("recuerda que me gusta el azul")
        console.handle("recuerdos")
        console.handle("jugar")
        console.handle("estado")

        assert any(line.startswith("Lo recordaré: que me gusta el azul") for line in output)
        assert any("Prometo no comérmelo" in line for line in output)
        assert "- que me gusta el azul" in output
        assert any("Qué divertido" in line for line in output)
        assert reactions == ["play"]
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


class FakeVisionService:
    def __init__(self, embeddings: list[list[float]]) -> None:
        self.last_embeddings = embeddings

    def observe_once(self) -> list[object]:
        return []


def test_console_guides_new_people_one_at_a_time() -> None:
    with tempfile.TemporaryDirectory() as directory:
        database_path = Path(directory) / "petbot.db"
        pet_repository = SQLitePetRepository(database_path)
        session = PetService(pet_repository).create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED)
        output: list[str] = []
        vision = FakeVisionService([[1.0, 0.0], [0.0, 1.0]])
        console = DevelopmentConsole(
            session=session,
            memory_service=MemoryService(SQLiteMemoryRepository(database_path)),
            personality_service=PersonalityService(pet_repository),
            people_service=PeopleService(SQLitePeopleRepository(database_path)),
            vision_service=vision,  # type: ignore[arg-type]
            output_fn=output.append,
        )

        console._handle_person_entered()
        assert "Quedan 2 personas nuevas" in output[-1]

        vision.last_embeddings = [[1.0, 0.0]]
        console.handle("listo")
        console.handle("me llamo Ana")
        console.handle("sí")

        assert any("Queda 1 persona nueva" in line for line in output)
        assert any("Guardaré una huella facial local" in line for line in output)


def test_console_does_not_greet_the_same_person_twice_immediately() -> None:
    with tempfile.TemporaryDirectory() as directory:
        database_path = Path(directory) / "petbot.db"
        pet_repository = SQLitePetRepository(database_path)
        session = PetService(pet_repository).create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED)
        console = DevelopmentConsole(session, MemoryService(SQLiteMemoryRepository(database_path)), PersonalityService(pet_repository))

        assert console._can_greet("Manuel")
        assert not console._can_greet("Manuel")


def test_touch_rest_recovers_energy() -> None:
    with tempfile.TemporaryDirectory() as directory:
        database_path = Path(directory) / "petbot.db"
        pet_repository = SQLitePetRepository(database_path)
        session = PetService(pet_repository).create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED)
        console = DevelopmentConsole(session, MemoryService(SQLiteMemoryRepository(database_path)), PersonalityService(pet_repository))
        before = console.personality_service.get_state(session.pet.id)[1].values

        console.rest_from_touch()

        after = console.personality_service.get_state(session.pet.id)[1].values
        assert after[Emotion.ENERGY] > before[Emotion.ENERGY]
        assert after[Emotion.STRESS] <= before[Emotion.STRESS]
