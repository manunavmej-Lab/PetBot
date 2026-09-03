# Fase 2.8 — Comunicación Raspberry Pi ↔ ESP32

## Objetivo
Permitir que el cerebro solicite movimientos sin controlar motores directamente.

## Flujo
`Brain -> Action -> BehaviorService -> SafetyValidator -> RobotController -> ESP32 -> Cytron -> motores`

## RobotController
- stop
- move_forward(speed)
- move_backward(speed)
- turn_left(speed)
- turn_right(speed)
- rotate(speed)
- get_status

Velocidad normalizada 0..1.

## Implementaciones
- SimulatedRobotController
- ESP32RobotController

## Protocolo
Ejemplo comando:
```json
{"v":1,"cmd":"MOVE","linear":0.2,"angular":0.0}
```

## Seguridad
- heartbeat;
- timeout -> STOP;
- rechazo de comando inválido;
- velocidad máxima configurable;
- STOP prioritario.

## Criterio de aceptación
Mismos tests de comportamiento con simulador y ESP32 real cambiando solo configuración.
