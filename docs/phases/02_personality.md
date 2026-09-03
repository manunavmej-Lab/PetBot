# Fase 2.2 — Personalidad y emociones

## Dependencia
Completar `01_pet_lifecycle.md`.

## Objetivo
Separar temperamento estable y estado emocional temporal.

## Personalidad
Rasgos 0..100:
- joy
- curiosity
- sociability
- affection
- playfulness
- calmness
- courage
- independence

Cada rasgo tendrá base, valor actual, mínimo y máximo.

## EmotionalState
- happiness
- energy
- curiosity
- surprise
- stress
- affection

## EvolutionEngine
Único componente autorizado para alterar personalidad.

Reglas:
- cambios pequeños;
- nunca fuera de límites;
- una interacción aislada no produce cambios grandes;
- registrar causa de cada cambio.

## Tests
- límites 0..100;
- personalidad persiste;
- emociones cambian sin alterar personalidad;
- evolución máxima por interacción;
- decaimiento funciona.

## Criterio de aceptación
Simular 100 interacciones sin producir valores inválidos y persistiendo correctamente la evolución.
