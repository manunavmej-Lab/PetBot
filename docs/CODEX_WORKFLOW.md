# Flujo recomendado con Codex en VS Code

## Regla principal
Dar a Codex una fase cada vez.

No pedir:
> Implementa PETBOT completo.

Pedir:
> Lee AGENTS.md, docs/ARCHITECTURE.md y docs/phases/01_pet_lifecycle.md. Implementa únicamente esa fase. Ejecuta los tests y resume los cambios.

## Prompt recomendado
```text
Lee primero:
- AGENTS.md
- docs/ARCHITECTURE.md
- docs/DATA_MODEL.md
- docs/phases/XX_....md

Implementa únicamente el alcance de esa fase.

Antes de modificar código:
1. resume el plan;
2. identifica archivos a crear/modificar;
3. no implementes funcionalidades fuera de alcance.

Después:
1. ejecuta tests;
2. corrige fallos;
3. actualiza README si es necesario;
4. informa de decisiones técnicas importantes.
```

## Secuencia
1. Implementar fase 01.
2. Revisar y commit.
3. Implementar fase 02.
4. Continuar de forma incremental.
