from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from petbot.domain.personality.traits import Trait, TraitValue


class PersonalityPreset(str, Enum):
    CALM = "tranquilo"
    BALANCED = "equilibrado"
    PLAYFUL = "jugueton"


PRESET_VALUES: dict[PersonalityPreset, dict[Trait, int]] = {
    PersonalityPreset.CALM: {Trait.JOY: 65, Trait.CURIOSITY: 65, Trait.SOCIABILITY: 60, Trait.AFFECTION: 75, Trait.PLAYFULNESS: 40, Trait.CALMNESS: 90, Trait.COURAGE: 50, Trait.INDEPENDENCE: 50},
    PersonalityPreset.BALANCED: {Trait.JOY: 75, Trait.CURIOSITY: 85, Trait.SOCIABILITY: 75, Trait.AFFECTION: 70, Trait.PLAYFULNESS: 65, Trait.CALMNESS: 60, Trait.COURAGE: 55, Trait.INDEPENDENCE: 45},
    PersonalityPreset.PLAYFUL: {Trait.JOY: 90, Trait.CURIOSITY: 90, Trait.SOCIABILITY: 80, Trait.AFFECTION: 75, Trait.PLAYFULNESS: 95, Trait.CALMNESS: 35, Trait.COURAGE: 65, Trait.INDEPENDENCE: 40},
}


@dataclass(frozen=True)
class Personality:
    preset: PersonalityPreset
    traits: Mapping[Trait, TraitValue]

    @property
    def values(self) -> Mapping[Trait, int]:
        """Compatibilidad: expone los valores actuales de cada rasgo."""
        return {trait: value.current_value for trait, value in self.traits.items()}

    @classmethod
    def from_preset(cls, preset: PersonalityPreset | str) -> "Personality":
        try:
            resolved_preset = PersonalityPreset(preset)
        except ValueError as error:
            raise ValueError(f"Preset de personalidad no válido: {preset}") from error
        return cls(preset=resolved_preset, traits={
            trait: TraitValue(base_value=value, current_value=value)
            for trait, value in PRESET_VALUES[resolved_preset].items()
        })
