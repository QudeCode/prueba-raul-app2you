# 0017 · Cada franja dice qué reservas la ocupan

Estado: aceptada
Tipo: decisión
Amplía: [0013](0013-disponibilidad-por-tramos.md)

## Contexto
El enunciado (punto 2) pide que la consulta de disponibilidad sepa «explicar per què no està disponible (quines reserves bloquegen)». La respuesta traía las reservas activas del día y las franjas por separado: para saber qué reserva bloquea una franja, el cliente tenía que cruzar las horas de unas y otras, repitiendo el cálculo de solapes que el backend ya hace al partir el día en tramos.

## Decisión
- **Cada `FranjaRespuesta` lleva `ocupada_por`:** los ids de las reservas activas que ocupan la franja, pendientes incluidas, en el orden de `reservas`. Las reservas completas siguen en `DisponibilidadRespuesta.reservas`, así que no se repiten.
- **Lo calcula la misma partición** (`tramos` en `reservas/service.py`): cada tramo guarda los ids de las ocupaciones que lo cubren.
- **Solo se fusionan los tramos vecinos con los mismos ocupantes** (que dan las mismas cargas). Así cada reserva de `ocupada_por` cubre la franja entera, y lo que diga una franja vale para cualquier selección dentro de ella. Si se fusionaran solo por cargas, dos pendientes contiguas formarían una franja con las dos, y el aviso de rechazos nombraría a las dos aunque la selección solo tocara una.
- **El frontend usa los ids en lugar de calcular solapes:** el aviso de las pendientes que rechazaría un responsable toma las que ocupan las franjas de la selección, y el timeline con aforo nombra a los ocupantes de cada franja.

## Alternativas descartadas
- Repetir las reservas completas en cada franja: duplica datos en la respuesta.
- Dejar el cruce al cliente: dos implementaciones del solapamiento que podrían divergir (el mismo motivo que en la 0013).
- Fusionar solo por cargas y unir los ocupantes: menos franjas, pero los ocupantes de una franja dejan de ser precisos.

## Consecuencias
- Con aforo compartido, una franja libre puede tener ocupantes: la capacidad libre ya los descuenta.
- Dos reservas contiguas con la misma carga se ven como dos franjas en lugar de una; el timeline sin aforo dibuja las reservas, no las franjas, así que no cambia.
