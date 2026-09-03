# Modelo de datos inicial

## Pet

Campos mínimos:

- `id: UUID`
- `name: str`
- `owner_name: str`
- `created_at: datetime`
- `is_active: bool`
- `schema_version: int`

## PersonalityTrait

- `pet_id`
- `trait`
- `base_value`
- `current_value`
- `min_value`
- `max_value`
- `updated_at`

Rasgos iniciales:

- joy
- curiosity
- sociability
- affection
- playfulness
- calmness
- courage
- independence

## EmotionalState

- happiness
- energy
- curiosity
- surprise
- stress
- affection

El estado emocional cambia rápido. La personalidad cambia lentamente.

## Memory

- `id`
- `pet_id`
- `type`
- `content`
- `importance`
- `confidence`
- `source`
- `created_at`
- `last_accessed_at`
- `expires_at` opcional

Tipos:

- semantic
- episodic
- relational
- temporary
- visual

## Relationship

- `pet_id`
- `person_id`
- `display_name`
- `trust`
- `affection`
- `familiarity`
- `last_interaction_at`
