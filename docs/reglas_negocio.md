# Reglas de negocio

## Conceptos
- **Reserva activa**: reserva en estado `PENDIENTE` o `APROBADA`. Solo las activas ocupan el recurso; `RECHAZADA` y `CANCELADA` lo liberan.
- **Franja de una reserva**: por horas, de `hora_inicio` a `hora_fin`; día completo, de 00:00 a 24:00 de su fecha.
- **Solapamiento**: dos franjas del mismo día se solapan si `inicio1 < fin2` y `inicio2 < fin1`. Cubre solapes parciales, totales y una contenida en otra.
- **Inicio de una reserva**: su fecha a la `hora_inicio`; en día completo, a las 00:00.

## Modalidad por tipo de recurso

| Tipo             | Modalidad              |
|------------------|------------------------|
| Sala de reunión  | Por horas              |
| Vehículo         | Día completo           |
| Equipo           | Por horas o día completo |

## Crear una reserva
1. Una reserva ocupa como máximo un día: una sola `fecha`. Para varios días hacen falta varias reservas.
2. La modalidad debe ser válida para el tipo de recurso.
   - Por horas: `hora_inicio` y `hora_fin` informadas, con `hora_inicio < hora_fin`. `hora_fin` es como muy tarde las 23:59.
   - Día completo: sin horas.
3. No se puede reservar en el pasado.
4. `asistentes_sala`: obligatorio y `>= 1` en salas con aforo compartido; vacío en el resto de recursos.
5. Sin aforo compartido: la franja no puede solaparse con ninguna reserva activa del recurso.
6. Con aforo compartido: en ningún momento de la franja la suma de `asistentes_sala` de las reservas activas puede superar `capacidadMaxima`. Se comprueba el momento de máxima ocupación, no la suma de todas las reservas que se solapan.
7. Estado inicial según el rol del titular:
   - Trabajador: `PENDIENTE`.
   - Responsable: `APROBADA`, con él mismo como aprobador.
8. Una reserva pendiente bloquea el recurso para todos, también para un responsable. Si un responsable quiere ese hueco, primero rechaza la pendiente y luego reserva.

## Aprobar o rechazar
9. Solo un responsable, y solo sobre reservas `PENDIENTE`.
10. Aprobar: pasa a `APROBADA` y se guarda quién la aprobó.
11. Rechazar: pasa a `RECHAZADA`.
12. Al aprobar no se vuelven a comprobar conflictos: la reserva pendiente ya bloqueaba su franja, así que nadie ha podido reservar encima.

## Cancelar o transferir
13. Solo el titular, y solo sobre reservas activas.
14. Los plazos se cuentan hasta el inicio de la reserva.
15. Según la política de cancelación del recurso:

| Política  | Cancelar             | Transferir                   |
|-----------|----------------------|------------------------------|
| Flexible  | Hasta 1h antes       | Hasta el inicio              |
| Moderada  | Hasta 24h antes      | Desde 24h antes hasta el inicio |
| Bloqueada | No                   | No                           |

16. Cancelar: pasa a `CANCELADA`.
17. Transferir: solo cambia el titular; el estado se mantiene.
18. Se puede transferir a cualquier usuario excepto al propio titular.
19. Una reserva que ya ha comenzado no se puede transferir.

## Consultar disponibilidad
20. Para un recurso y una fecha se devuelve:
   - Las reservas activas de ese día, con su estado (explican por qué no está disponible).
   - Por horas: las franjas libres dentro del día (00:00–24:00).
   - Día completo: si está disponible o no.
   - Con aforo compartido: la capacidad libre en cada franja.
