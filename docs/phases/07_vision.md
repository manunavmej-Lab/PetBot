# Fase 2.7 — Visión

## Objetivo
Integrar cámara como sistema de percepción, no como cerebro.

## Hardware
Raspberry Pi Camera Module 3 Wide.

## Interfaces
- Camera
- VisionDetector

## Eventos iniciales
- PERSON_DETECTED
- FACE_DETECTED
- OBJECT_DETECTED
- PERSON_ENTERED_VIEW
- PERSON_LEFT_VIEW

## Reglas
- procesar localmente cuando sea razonable;
- no enviar vídeo continuo a IA;
- convertir percepción en eventos/contexto;
- guardar memoria visual solo cuando proceda.

## Simulación
Webcam o imágenes de test.

## Criterio de aceptación
Detectar una persona y producir evento consumible por EventBus/Brain.
