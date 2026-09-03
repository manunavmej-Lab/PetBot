# Fase 2.6 — Voz

## Objetivo
Añadir entrada y salida por voz sin acoplar el cerebro al hardware.

## Interfaces
- Microphone
- SpeechToText
- TextToSpeech
- Speaker

## Implementaciones
### simulation/mac
Dispositivos de audio del Mac.

### raspberry
- micrófono USB SunFounder;
- MAX98357A I2S;
- altavoz 4Ω 3W.

## Flujo
`audio -> STT -> texto -> Brain -> TTS -> Speaker`

## Requisitos
- activación manual en simulación inicialmente;
- no escuchar mientras PETBOT habla en primera versión;
- estados escucha/habla reflejables en FaceDisplay.

## Criterio de aceptación
Usuario habla, PETBOT responde por audio y cambia expresión.
