# Arquitectura de PETBOT

## 1. Separación conceptual

PETBOT se divide en:

- **Cuerpo**: hardware físico.
- **Mascota**: identidad, personalidad, recuerdos y relaciones.
- **Cerebro**: lógica que interpreta contexto y decide acciones.
- **Adaptadores**: hardware real o simulaciones.

La mascota debe poder trasladarse a otro hardware sin perder su identidad.

## 2. Capas

### Domain

No conoce hardware ni frameworks.

Incluye:

- Pet
- Identity
- Personality
- EmotionalState
- Memory
- Relationship
- Behavior/Action

### Application / Services

Orquesta casos de uso:

- crear mascota;
- cargar mascota;
- recordar;
- olvidar;
- procesar interacción;
- evolucionar personalidad;
- decidir respuesta.

### Interfaces

Contratos abstractos:

- FaceDisplay
- Microphone
- Speaker
- Camera
- RobotController
- AIProvider
- PetRepository
- MemoryRepository

### Infrastructure

Implementaciones concretas:

- SQLite
- modelo IA cloud/local
- pantalla de escritorio
- Waveshare
- micrófono Mac/USB
- cámara simulada/Raspberry
- comunicación ESP32

## 3. Event Bus

PETBOT será dirigido por eventos.

Eventos previstos:

```text
PET_CREATED
PET_LOADED
USER_SPOKE
MEMORY_CREATED
MEMORY_RECALLED
PERSON_DETECTED
OBJECT_DETECTED
EXPRESSION_CHANGED
CONTROLLER_CONNECTED
MOVE_REQUESTED
MOVE_COMPLETED
BATTERY_LOW
BUMPER_PRESSED
```

En primeras fases basta un EventBus en memoria.

## 4. Acciones

La IA no controla hardware directamente.

Catálogo inicial:

```text
SPEAK
SET_EXPRESSION
BLINK
LOOK_LEFT
LOOK_RIGHT
MOVE_FORWARD
MOVE_BACKWARD
TURN_LEFT
TURN_RIGHT
STOP
REMEMBER
FORGET
```

Fase 3 añadirá:

```text
FOLLOW_PERSON
GO_TO
DOCK
```

Todas las acciones deben validarse antes de ejecutarse.

## 5. Modos

### simulation

Mac/PC:

- cara en ventana;
- audio local;
- cámara opcional del ordenador;
- movimiento simulado por consola/log.

### raspberry

Hardware real:

- Waveshare 4.3";
- Camera Module 3 Wide;
- micrófono USB;
- MAX98357A + altavoz;
- comunicación ESP32.

La lógica del dominio debe ser idéntica en ambos modos.

## 6. Persistencia

SQLite.

Base sugerida:

```text
pets
personality_traits
emotional_state
memories
relationships
preferences
interaction_events
settings
```

Aplicar migraciones versionadas.

## 7. Seguridad de movimientos

La Raspberry solicita movimiento.

El ESP32 ejecuta bajo límites físicos.

La IA nunca enviará PWM directo.

Ejemplo:

```text
AI -> Action(MOVE_FORWARD, speed=0.2, duration=1.0)
Validator -> RobotController
RobotController -> ESP32
ESP32 -> Cytron
```


---

## 8. Canales de interacción

PETBOT debe soportar múltiples canales sobre el mismo cerebro, personalidad y memoria.

Canales previstos:

- voz local;
- interfaz de texto de desarrollo;
- WhatsApp;
- futuros canales opcionales.

Los canales implementan una interfaz común y no contienen lógica propia de personalidad o memoria.

WhatsApp se implementará mediante la API oficial y las acciones físicas remotas estarán bloqueadas por defecto hasta disponer de autorización específica.
