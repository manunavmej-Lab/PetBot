from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from petbot.domain.personality.emotions import Emotion
from petbot.domain.personality.evolution import EvolutionEngine, PersonalityChange
from petbot.domain.personality.personality import Personality, PersonalityPreset
from petbot.domain.personality.traits import Trait
from petbot.infrastructure.database.pet_repository import SQLitePetRepository
from petbot.services.personality_service import PersonalityService
from petbot.services.pet_service import PetService


@pytest.fixture
def services() -> tuple[PetService, PersonalityService]:
    with tempfile.TemporaryDirectory() as temporary_directory:
        repository = SQLitePetRepository(Path(temporary_directory) / "petbot.db")
        yield PetService(repository), PersonalityService(repository)


def test_trait_values_never_escape_limits() -> None:
    personality = Personality.from_preset(PersonalityPreset.CALM)
    engine = EvolutionEngine()

    for _ in range(100):
        personality = engine.evolve(personality, [PersonalityChange(Trait.CALMNESS, 2, "interacción positiva")])

    assert personality.traits[Trait.CALMNESS].current_value == 100


def test_emotions_change_without_changing_personality(services: tuple[PetService, PersonalityService]) -> None:
    pet_service, personality_service = services
    session = pet_service.create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED)

    personality, emotions = personality_service.process_interaction(
        session.pet.id, emotional_changes={Emotion.HAPPINESS: 20}, personality_changes=[]
    )

    assert emotions.values[Emotion.HAPPINESS] == 70
    assert personality.values[Trait.JOY] == 75


def test_evolution_is_persisted_with_its_cause(services: tuple[PetService, PersonalityService]) -> None:
    pet_service, personality_service = services
    session = pet_service.create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED)

    personality_service.process_interaction(
        session.pet.id,
        emotional_changes={},
        personality_changes=[PersonalityChange(Trait.CURIOSITY, 2, "exploró una habitación")],
    )

    reloaded = pet_service.load_active()
    assert reloaded is not None
    assert reloaded.personality.traits[Trait.CURIOSITY].current_value == 87


def test_change_larger_than_interaction_limit_is_rejected() -> None:
    with pytest.raises(ValueError, match="máximo"):
        PersonalityChange(Trait.JOY, 3, "cambio excesivo")


def test_emotional_decay_returns_to_baseline(services: tuple[PetService, PersonalityService]) -> None:
    pet_service, personality_service = services
    session = pet_service.create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED)
    personality_service.process_interaction(session.pet.id, emotional_changes={Emotion.STRESS: 10}, personality_changes=[])

    state = personality_service.decay_emotions(session.pet.id, amount=4)

    assert state.values[Emotion.STRESS] == 6


def test_one_hundred_interactions_remain_valid_and_persist(services: tuple[PetService, PersonalityService]) -> None:
    pet_service, personality_service = services
    session = pet_service.create_active(name="Boti", owner_name="Manuel", preset=PersonalityPreset.BALANCED)

    for index in range(100):
        personality_service.process_interaction(
            session.pet.id,
            emotional_changes={Emotion.ENERGY: 2 if index % 2 == 0 else -2},
            personality_changes=[PersonalityChange(Trait.JOY, 2 if index % 2 == 0 else -2, "interacción simulada")],
        )

    loaded = pet_service.load_active()
    assert loaded is not None
    assert all(0 <= value.current_value <= 100 for value in loaded.personality.traits.values())
    assert loaded.personality.traits[Trait.JOY].current_value == 75
