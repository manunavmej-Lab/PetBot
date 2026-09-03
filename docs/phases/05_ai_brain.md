# Fase 2.5 — Cerebro IA

## Objetivo
Introducir IA conversacional manteniendo el control del sistema.

## Regla principal
La IA NO modifica código, no escribe directamente DB, no controla GPIO, no ejecuta shell y no decide PWM.

Devuelve una `BrainDecision` validable.

## Entrada
- texto del usuario;
- personalidad;
- estado emocional;
- recuerdos relevantes;
- contexto reciente;
- eventos perceptivos relevantes.

## Salida estructurada
```json
{
  "speech": "¡Estoy genial!",
  "emotion": "happy",
  "expression": "wink",
  "actions": [],
  "memory_candidates": []
}
```

## Contrato AIProvider
Permitir proveedor cloud, proveedor local futuro y fake provider para tests.

## Validación
Crear `DecisionValidator`. Toda acción debe existir en catálogo permitido.

## Tests
- respuesta válida;
- JSON inválido;
- acción desconocida;
- timeout;
- proveedor caído;
- respuesta sin speech.

## Criterio de aceptación
Conversación en modo texto usando nombre, personalidad y memoria persistida.
