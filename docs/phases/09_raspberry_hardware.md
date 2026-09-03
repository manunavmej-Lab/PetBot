# Fase 2.9 — Integración Raspberry Pi 5

## Hardware conocido
- Raspberry Pi 5 8GB;
- NVMe 64GB;
- refrigeración activa;
- Waveshare 4.3" DSI 800x480;
- Camera Module 3 Wide;
- micrófono USB SunFounder;
- MAX98357A;
- altavoz CQRobot 4Ω 3W;
- DC-DC 12/24V -> 5V 5A 25W USB-C.

## Objetivo
Sustituir adaptadores simulados por hardware real manteniendo intacto el dominio.

## Configuración
```text
PETBOT_MODE=raspberry
DISPLAY_DRIVER=waveshare
CAMERA_DRIVER=picamera
MICROPHONE_DRIVER=usb
SPEAKER_DRIVER=i2s
ROBOT_DRIVER=esp32
```

## Secuencia
1. Raspberry/NVMe;
2. pantalla;
3. cámara;
4. micrófono;
5. audio;
6. DC-DC;
7. puente ESP32;
8. prueba integrada.

## Criterio de aceptación
Arrancar PETBOT en Raspberry y ejecutar conversación completa con cara, voz y memoria.
