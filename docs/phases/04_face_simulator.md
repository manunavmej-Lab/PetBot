# Fase 2.4 — Cara simulada

## Objetivo
Desarrollar en Mac/PC la cara de PETBOT antes de usar la Waveshare 4.3" 800x480.

La pantalla mostrará ojos, nariz y boca como gráficos.

## Contrato
`FaceDisplay` con operaciones:
- set_expression
- blink
- wink_left
- wink_right
- look_at
- set_mouth_state
- speak_animation
- sleep
- wake

## Simulación
Implementar `DesktopFaceDisplay` a resolución lógica 800x480.

## Expresiones iniciales
- neutral
- happy
- excited
- sad
- sleepy
- surprised
- confused
- annoyed

## Requerimientos
- animaciones no bloqueantes;
- permitir combinar habla/parpadeo;
- separar assets de lógica;
- dominio desacoplado de la librería gráfica.

## Criterio de aceptación
Demo que ejecuta expresiones, mirada, guiño y animación de habla.
