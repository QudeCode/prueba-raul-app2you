# 0013 · Disponibilidad por tramos y reservas serializadas

Estado: aceptada
Tipo: ADR

## Contexto
La disponibilidad de un recurso en un día (regla 20) y la validación al crear (reglas 5 y 6) responden a la misma pregunta: cuánto está ocupado el recurso en cada momento del día. Con aforo compartido no basta con buscar solapes: cuenta el momento de máxima ocupación, no la suma de todas las reservas que se solapan. Además, dos peticiones simultáneas no pueden reservar a la vez el mismo hueco, y dos acciones simultáneas sobre la misma reserva no pueden pisarse.

## Decisión
- **El día reservable por horas va de 00:00 a 23:59.** La franja por horas acaba como muy tarde a las 23:59 (regla 2); el día completo conserva 00:00–24:00 y ocupa el día entero. La disponibilidad trabaja en la ventana semiabierta `[00:00, 23:59)`, y la última franja libre termina a las 23:59: nunca aparece un hueco «23:59–24:00» que no se podría reservar.
- **La ocupación del día es una partición en tramos** (`tramos` en `reservas/service.py`): los inicios y fines de las reservas activas cortan la ventana en tramos consecutivos, y cada tramo suma la ocupación de las reservas que lo cubren (1 por reserva sin aforo compartido, `asistentes_sala` con aforo). Los tramos vecinos iguales se fusionan (desde la [0017](0017-franjas-con-sus-reservas.md), los que tienen los mismos ocupantes).
- **La misma partición responde a la regla 20 y valida las reglas 5 y 6.** El máximo de los tramos que cubre una franja nueva es su momento de máxima ocupación. Una sola implementación para consultar y para validar, así que no pueden discrepar.
- **Las reservas de un recurso se serializan:** al crear, el servicio bloquea la fila del recurso (`SELECT … FOR UPDATE`) antes de comprobar conflictos y la libera con el commit.
- **Las acciones bloquean la reserva:** aprobar, rechazar, cancelar y transferir la leen con `FOR UPDATE OF reserva` antes de comprobar su estado, así que la segunda acción ve lo que dejó la primera.
- **Los plazos se calculan solo en el backend,** con la hora local del servidor (`datetime.now()`, sin zona, como `fecha` y `hora_*`). Cada `ReservaRespuesta` lleva `puede_cancelar` y `puede_transferir`, y el frontend solo los muestra.

## Alternativas descartadas
- Una restricción `EXCLUDE` de PostgreSQL con rangos: garantiza la ausencia de solapes en la base, pero no puede expresar el aforo compartido (regla 6).
- Comprobar sin bloqueo: dos peticiones simultáneas pasan las dos la comprobación y se crean reservas solapadas.
- Nivel de aislamiento `SERIALIZABLE`: obliga a reintentar las transacciones que fallan, y el bloqueo de una fila basta.
- Repetir los plazos en el frontend: dos implementaciones de las reglas 14, 15 y 19 que podrían divergir.
- Horas como minutos 0–1440 en la API: ya descartado en la decisión 0004.

## Consecuencias
- Consulta y validación coinciden siempre: lo que la disponibilidad muestra como libre se puede reservar, salvo que alguien reserve antes.
- Las reservas del mismo recurso esperan unas a otras durante la validación; las de recursos distintos no.
- El bloqueo solo protege si todo el trabajo de una petición usa la misma sesión: FastAPI comparte `get_session` dentro de una petición, y el seed construye los servicios sobre una misma sesión.
- Backend y navegador deben compartir zona horaria. Se cumple en local; en un despliegue, los plazos se desplazarían.
- `puede_cancelar` y `puede_transferir` valen para el momento de la respuesta: si caducan con la página abierta, la acción responde 409 y el mensaje se ve.
