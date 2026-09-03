# PETBOT

Proyecto del cerebro software de PETBOT.

## Meta

Construir una mascota robótica que:

- tenga identidad propia;
- mantenga una personalidad base;
- evolucione lentamente a partir de interacciones;
- recuerde información y experiencias;
- muestre expresiones en pantalla;
- escuche y hable;
- use cámara;
- pueda ordenar movimientos al ESP32;
- evolucione en una fase posterior hacia navegación autónoma.

## Desarrollo

El proyecto debe poder ejecutarse primero en macOS/PC en modo simulación y posteriormente en Raspberry Pi 5.

## Primer arranque (fase 1)

Requiere Python 3.12 o superior. Crea un entorno virtual e instala el proyecto:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install ".[dev]"
```

Para iniciar PETBOT:

```bash
python -m petbot.main
```

Al iniciar, se abre la cara simulada con una expresión neutral. La consola queda disponible en la terminal y las interacciones, como `jugar`, producen una reacción visual.


En el primer arranque se solicitan el nombre de la mascota, el propietario y el preset de personalidad. Los datos se guardan en `data/petbot.db`; en ejecuciones siguientes se carga la mascota activa.

La consola de desarrollo permite probar el cerebro sin voz ni hardware:

```text
PETBOT > ayuda
PETBOT > manual
PETBOT > recuerda que me gusta el azul
PETBOT > recuerdos
PETBOT > jugar
PETBOT > estado
PETBOT > salir
```

También puedes escribir frases normales en el modo simulado, por ejemplo `hola`, `estoy triste` o `me gusta dormir al sol`. Buvi responderá en texto, cambiará su expresión y, en el último caso, propondrá y guardará un recuerdo.

En macOS, la mascota escucha desde el inicio. Tras conceder los permisos de micrófono y reconocimiento de voz, di su nombre en cualquier parte de la frase para activarla: `Bulvi, hola`, `hola Bulvi` o `estoy triste, Bulvi`. Las frases sin su nombre se ignoran. El comando `hablar` sigue disponible para una prueba manual.

Para ejecutar las pruebas:

```bash
pytest
```

## Cara simulada

Para abrir la demo de la cara de PETBOT en una ventana de 800×480:

```bash
python -m petbot.infrastructure.face.demo
```

## Orden de implementación

1. `docs/phases/01_pet_lifecycle.md`
2. `docs/phases/02_personality.md`
3. `docs/phases/03_memory.md`
4. `docs/phases/04_face_simulator.md`
5. `docs/phases/05_ai_brain.md`
6. `docs/phases/06_voice.md`
7. `docs/phases/07_vision.md`
8. `docs/phases/08_esp32_bridge.md`
9. `docs/phases/09_raspberry_hardware.md`
10. `docs/phases/10_navigation_phase3.md`
11. `docs/phases/11_whatsapp_channel.md`

Leer primero `AGENTS.md` y `docs/ARCHITECTURE.md`.
