from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Identity:
    """Datos estables que identifican a una mascota y a su propietario."""

    name: str
    owner_name: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("El nombre de la mascota no puede estar vacío.")
        if not self.owner_name.strip():
            raise ValueError("El nombre del propietario no puede estar vacío.")
