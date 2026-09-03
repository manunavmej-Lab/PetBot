# Fase 3 — Navegación autónoma

## Estado
No implementar hasta completar Fase 2.

## Objetivo
PETBOT debe conocer su entorno y desplazarse de forma autónoma.

## Hardware previsto
- LiDAR 360°;
- IMU;
- ToF frontales/laterales;
- sensores anticaída;
- encoders de Fase 1;
- cámara de Fase 2.

## Software previsto
```text
navigation/
├── localization.py
├── mapping.py
├── planner.py
├── obstacle_avoidance.py
└── docking.py
```

## Principio
La IA solicita metas como `GO_TO("salon")` o `FOLLOW_PERSON(person_id)`.
El sistema de navegación decide trayectorias.
La IA nunca controla ruedas individualmente.
