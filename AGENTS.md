# AGENTS.md — PETBOT

## Objetivo del repositorio

PETBOT es una plataforma robótica modular dividida en tres grandes fases:

1. **Fase 1 — Movimiento**: ESP32-S3, Cytron, motores, encoders y control manual.
2. **Fase 2 — Mascota inteligente**: identidad, personalidad, memoria, cara, voz, visión, IA y comunicación con el ESP32.
3. **Fase 3 — Navegación autónoma**: sensores, localización, SLAM, planificación y desplazamiento autónomo.

Este repositorio Python corresponde principalmente al **cerebro de PETBOT ejecutado en Raspberry Pi 5**, pero debe poder desarrollarse y probarse en macOS/PC mediante simuladores.

## Principios obligatorios

- Python 3.12+.
- Código bajo `src/petbot/`.
- Arquitectura modular; evitar `main.py` gigantes.
- El dominio no puede depender directamente de Raspberry Pi, GPIO, cámara, pantalla ni ESP32.
- Todo hardware debe estar detrás de interfaces/adaptadores.
- Debe existir `simulation` y `raspberry` como modos de ejecución.
- SQLite será la persistencia inicial.
- Las claves y secretos van en `.env`; nunca en Git.
- Añadir tests para cada caso de uso.
- Los módulos deben tener typing.
- Preferir dataclasses, enums y Protocol/ABC para contratos simples.
- No permitir que un modelo de IA ejecute directamente comandos físicos.
- Toda acción física debe pasar por validación y catálogo de acciones permitidas.
- La mascota es una entidad persistente independiente del hardware.

## Flujo de trabajo para Codex

Antes de implementar una fase:

1. Leer `docs/ARCHITECTURE.md`.
2. Leer el fichero de fase correspondiente en `docs/phases/`.
3. Implementar solamente el alcance de esa fase.
4. Ejecutar tests.
5. Actualizar `README.md` si cambia el uso.
6. No adelantar funcionalidades de fases posteriores salvo contratos/interfaces mínimos.

## Estructura objetivo

```text
PETBOT/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── .env.example
├── src/
│   └── petbot/
│       ├── main.py
│       ├── application/
│       ├── domain/
│       ├── services/
│       ├── interfaces/
│       ├── infrastructure/
│       └── config/
├── data/
└── tests/
```

## Criterio global de calidad

Una fase está terminada cuando:

- cumple sus criterios de aceptación;
- tiene tests;
- funciona en modo simulación cuando corresponda;
- no rompe fases anteriores;
- no mezcla dominio con infraestructura;
- persiste correctamente los datos necesarios;
- documenta cómo ejecutarla.
