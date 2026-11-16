# 0004 · Enums como StrEnum y CHECK en la base de datos

Estado: aceptada
Tipo: decisión

## Contexto
Los estados, roles, tipos y políticas son conjuntos cerrados de valores. Además, hay invariantes de una sola fila (horas, capacidad, aprobador) que no deberían depender solo de la API.

## Decisión
- Los enums son `StrEnum` con el valor igual al nombre (`PENDIENTE = "PENDIENTE"`). Se guardan como `VARCHAR` con un `CHECK` generado desde el propio enum (`check_enum`).
- Cada invariante de una sola fila lleva un `CHECK` con nombre, además de la validación en el DTO o el servicio.
- Las horas son `TIME`. Una reserva por horas acaba como muy tarde a las 23:59, porque Python no puede representar las 24:00.

## Alternativas descartadas
- Tipos ENUM nativos de PostgreSQL: más difíciles de cambiar y sin ventaja aquí.
- Guardar las horas en minutos (0 a 1440): exacto, pero obliga a convertir en la API y en los diagramas.

## Consecuencias
- Un INSERT que se salte la API no puede dejar datos incoherentes de una fila.
- Las reglas que cruzan tablas (modalidad según tipo, asistentes solo en salas con aforo compartido) viven en el servicio.
