# Fase 2.10 — Canal WhatsApp

## Objetivo

Permitir que el propietario se comunique con la misma mascota PETBOT mediante WhatsApp, usando la misma identidad, personalidad, memoria y cerebro que en la interacción física.

## Principio de arquitectura

WhatsApp es un canal de entrada/salida, no un cerebro independiente.

```text
WhatsApp
   ↓
MessagingChannel
   ↓
ConversationService
   ↓
Brain + Memory + Personality
   ↓
MessagingChannel
   ↓
WhatsApp
```

## Requisitos funcionales

### RF-01 — Recibir mensajes

Recibir mensajes del propietario mediante la API oficial de WhatsApp Business Platform / Cloud API.

### RF-02 — Identificar al propietario

Solo procesar como propietario los números/contactos autorizados.

No confiar únicamente en el texto del mensaje para identificar al usuario.

### RF-03 — Usar la misma mascota

Los mensajes de WhatsApp deben usar:

- la mascota activa;
- su personalidad actual;
- sus recuerdos;
- sus relaciones;
- el mismo Brain que usa voz/pantalla.

No crear una mascota separada para WhatsApp.

### RF-04 — Responder

Permitir inicialmente respuestas de texto.

Diseñar interfaces para soportar en el futuro:

- imágenes;
- audio;
- eventos/alertas.

### RF-05 — Memoria

Una conversación por WhatsApp puede:

- consultar recuerdos;
- crear recuerdos si corresponde;
- ejecutar `REMEMBER` y `FORGET` bajo las mismas reglas que la conversación por voz.

### RF-06 — Contexto de canal

El Brain debe saber que el mensaje llega por `whatsapp`, para evitar respuestas que dependan de que el usuario esté físicamente delante del robot.

## Seguridad

Las acciones remotas deben clasificarse.

### Permitidas inicialmente

- conversar;
- consultar memoria;
- consultar estado de PETBOT;
- recibir notificaciones.

### Requieren autorización adicional

- mover el robot;
- activar cámara;
- obtener imágenes;
- acceder a sensores;
- ejecutar acciones físicas.

No implementar control físico remoto hasta disponer de autenticación, autorización, límites y auditoría.

## Interfaces

Crear una abstracción:

```text
MessagingChannel
```

Operaciones mínimas:

- receive_message
- send_text
- send_media (contrato futuro)
- identify_sender

Implementación:

```text
infrastructure/whatsapp/
    whatsapp_cloud_api.py
```

## Eventos

Añadir:

```text
MESSAGE_RECEIVED
MESSAGE_SENT
REMOTE_COMMAND_REQUESTED
REMOTE_COMMAND_REJECTED
```

## Configuración

Secretos solo en `.env`.

Ejemplo conceptual:

```text
WHATSAPP_ENABLED=false
WHATSAPP_ACCESS_TOKEN=...
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_VERIFY_TOKEN=...
```

Nunca guardar tokens en Git.

## Tests

- mensaje de propietario autorizado;
- remitente no autorizado;
- respuesta usa la mascota activa;
- memoria compartida con conversación local;
- acción física remota rechazada por defecto;
- fallo de API controlado;
- token/configuración ausente.

## Criterio de aceptación

Desde WhatsApp, el propietario puede mantener una conversación de texto con PETBOT y consultar un recuerdo creado previamente por otro canal, sin duplicar identidad ni memoria.
