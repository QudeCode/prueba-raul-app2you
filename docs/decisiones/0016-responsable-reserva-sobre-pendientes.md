# 0016 · Un responsable reserva sobre pendientes

Estado: aceptada
Tipo: ADR
Amplía: [0013](0013-disponibilidad-por-tramos.md)

## Contexto
El enunciado (punto 4) dice: «Un responsable pot reservar directament sense necessitat d'aprovació, inclús si el recurs està pendent d'aprovació». La primera versión de la regla 8 decía lo contrario: una pendiente bloqueaba también a los responsables, que tenían que rechazarla antes de reservar. Hay que decidir qué pasa con las pendientes que estorban, sobre todo en salas con aforo compartido, donde no siempre estorban todas las que se solapan.

## Decisión
- **A un responsable solo le bloquean las aprobadas** (reglas 5 y 6 contando solo las `APROBADA`). Si no cabe ni así, 409 sin tocar nada, y el mensaje nombra solo las aprobadas.
- **Las pendientes que estorban se rechazan al crear, en la misma transacción.** Si la franja cabe contando las pendientes, no se rechaza ninguna. Si no, en cada vuelta se toma el momento de máxima ocupación de la franja y se rechaza la pendiente más reciente (`creada_en`, y el `id` si empatan) de las que lo ocupan, hasta que quepa. Sin aforo compartido se trata como capacidad 1 con ocupación 1 por reserva, así que se rechazan todas las solapadas.
- **Las candidatas se buscan en un punto, no en el tramo.** La partición fusiona los tramos vecinos con la misma carga, así que un tramo puede estar hecho de varias pendientes contiguas sin que ninguna lo cubra entero. Las candidatas son las pendientes que ocupan el punto `max(inicio del tramo, inicio de la franja)`: siempre hay alguna y siempre se solapa con la franja nueva, así que nunca se rechaza una contigua que no estorba. Desde la [0017](0017-franjas-con-sus-reservas.md) los tramos ya no mezclan ocupantes distintos, y buscar en un punto sigue siendo correcto.
- **Una sola función pura,** `pendientes_a_rechazar` en `reservas/service.py`, sobre la misma partición en tramos de la 0013. Cada tramo lleva ahora dos cargas: con y sin pendientes.
- **Crear bloquea también las reservas activas del día** (del rango, en una reserva de varios días: decisión 0018) (`FOR UPDATE OF reserva`, con `populate_existing`), después del recurso. Sin eso, si un responsable reserva sobre una pendiente mientras otro la aprueba, el rechazo pisaría la aprobación y quedarían dos aprobadas solapadas. Las acciones solo bloquean su reserva, así que el orden de bloqueo no puede cruzarse.
- **La respuesta de crear es `ReservaCreadaRespuesta`:** la reserva y `rechazadas`, las pendientes rechazadas en el orden en que se rechazaron. Hereda de `ReservaRespuesta`, así que los clientes que solo leen la reserva no cambian.
- **La disponibilidad trae también la vista sin pendientes** (`libre_sin_pendientes`, `capacidad_libre_sin_pendientes` y `dia_completo_libre_sin_pendientes`). Sigue siendo pública y no depende de quién pregunta: el frontend usa esta vista cuando el usuario es responsable y avisa antes de confirmar de qué pendientes se rechazarán.

## Alternativas descartadas
- Rechazar todas las pendientes solapadas también con aforo: rechaza reservas que caben.
- Rechazar primero la más antigua: la más reciente es la que menos tiempo lleva planificada.
- Dejar las pendientes sin rechazar: al aprobarlas después se superaría la capacidad, y habría que volver a comprobar conflictos al aprobar (contra la regla 12).
- Calcular la vista del responsable en el frontend: duplicaría la partición del día.
- Un endpoint para previsualizar los rechazos: otra ruta para lo que ya dicen la vista sin pendientes y la respuesta de crear.

## Consecuencias
- El calendario mensual sigue contando las pendientes: un vehículo con solo pendientes se ve «Ocupado» aunque un responsable pueda reservarlo al abrir el día.
- Con aforo, el aviso previo del modal da las pendientes candidatas («las necesarias entre…»); la lista exacta llega en la respuesta y se muestra en el aviso de la página.
- Las reservas del mismo día de un recurso se bloquean mientras se crea una reserva; las acciones sobre ellas esperan a que termine.
- Al fusionar solo los tramos con las dos cargas iguales, un trabajador puede ver partida en dos una franja ocupada (una parte con pendiente y otra con aprobada).
