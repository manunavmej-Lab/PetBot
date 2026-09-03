# Fase 2.1 — Ciclo de vida de la mascota

## Objetivo

Implementar el primer flujo funcional de PETBOT:

```text
INICIO
  ↓
¿Existe mascota activa?
  ├─ NO → asistente de creación
  │        ↓
  │      guardar
  │        ↓
  └────→ cargar mascota
           ↓
        PETBOT listo
```

Esta fase NO incluye IA, voz, cámara, memoria avanzada ni motores.

## Requerimientos funcionales

### RF-01 — Detectar mascota

Al iniciar:

1. consultar `PetRepository`;
2. si hay una mascota activa, cargarla;
3. si no existe, iniciar creación.

### RF-02 — Crear mascota

Solicitar inicialmente:

- nombre de la mascota;
- nombre del propietario;
- estilo inicial:
  - tranquilo;
  - equilibrado;
  - juguetón.

No pedir demasiados datos. El resto se aprenderá después.

### RF-03 — Personalidad inicial

Crear valores base a partir del preset elegido.

Ejemplo equilibrado:

```text
joy=75
curiosity=85
sociability=75
affection=70
playfulness=65
calmness=60
courage=55
independence=45
```

### RF-04 — Persistir

Guardar la mascota y personalidad en SQLite.

### RF-05 — Reinicio

En la siguiente ejecución:

- NO volver a preguntar datos;
- cargar la misma mascota;
- mostrar un mensaje: `Hola, soy <nombre>.`

### RF-06 — Varias mascotas

El diseño de repositorio debe soportar varias mascotas aunque la UI inicial solo trabaje con una activa.

## Requerimientos técnicos

Crear como mínimo:

```text
src/petbot/
├── main.py
├── domain/pet/
│   ├── pet.py
│   ├── identity.py
│   └── repository.py
├── domain/personality/
│   ├── personality.py
│   └── traits.py
├── services/
│   └── pet_service.py
└── infrastructure/database/
    ├── sqlite.py
    └── pet_repository.py
```

Usar UUID y timestamps UTC.

## CLI provisional

Primera ejecución:

```text
PETBOT no tiene mascota creada.

¿Cómo quieres que se llame? Boti
¿Cómo te llamas? Manuel

Personalidad inicial:
1. Tranquilo
2. Equilibrado
3. Juguetón

> 2

Mascota creada.
Hola Manuel. Soy Boti.
```

Segunda ejecución:

```text
Cargando mascota...
Hola Manuel. Soy Boti.
```

## Tests obligatorios

- crea mascota si no existe;
- carga mascota si existe;
- no duplica mascota en segundo arranque;
- persiste nombre;
- persiste propietario;
- persiste personalidad;
- solo una mascota puede estar activa;
- preset inválido produce error controlado.

## Criterios de aceptación

La fase está terminada cuando:

1. `python -m petbot.main` funciona;
2. primera ejecución crea mascota;
3. segunda ejecución carga mascota;
4. la información sigue existiendo tras cerrar el programa;
5. todos los tests pasan.

## Fuera de alcance

- memoria;
- evolución real de personalidad;
- IA;
- pantalla;
- voz;
- cámara;
- ESP32.
