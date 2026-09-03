# Fase 2.3 — Memoria

## Objetivo
PETBOT debe recordar información útil sin guardar indiscriminadamente todo.

## Tipos
- semantic
- episodic
- relational
- temporary
- visual

## Requerimientos
Cada memoria tendrá contenido, tipo, importancia 0..1, confianza 0..1, origen, timestamps y expiración opcional.

## Casos de uso
- REMEMBER
- RECALL
- FORGET
- consolidación
- deduplicación básica

## Persistencia
SQLite. Preparar interfaz para búsqueda semántica futura.

## Tests
- guardar;
- recuperar;
- olvidar;
- expiración;
- aislamiento entre mascotas;
- deduplicación.

## Criterio de aceptación
Tras reiniciar, PETBOT recupera un recuerdo guardado en una ejecución anterior.
