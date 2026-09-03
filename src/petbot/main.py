from __future__ import annotations

import os
from pathlib import Path

from petbot.domain.personality.personality import PersonalityPreset
from petbot.infrastructure.database.pet_repository import SQLitePetRepository
from petbot.services.pet_service import PetService


def main() -> None:
    database_path = Path(os.environ.get("PETBOT_DATABASE_PATH", "data/petbot.db"))
    service = PetService(SQLitePetRepository(database_path))
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
