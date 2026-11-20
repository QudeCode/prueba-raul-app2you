# 0018 · Reservas de varios días

Estado: aceptada
Tipo: ADR
Amplía: [0013](0013-disponibilidad-por-tramos.md)

## Contexto
El enunciado dice que los vehículos se reservan «per dies complets» y los equipos «per hores o dies sencers». La primera versión de la regla 1 limitaba cada reserva a un día: llevarse la furgoneta de lunes a miércoles eran tres reservas, cada una con su aprobación, sin garantía de conseguir los tres días ni forma de cancelarlas juntas.

## Decisión
- **Una reserva de día completo es un rango de días seguidos:** `fecha` (el primero) y `fecha_fin` (el último). Una de un día tiene las dos iguales. Por horas sigue siendo de un día (`CHECK ck_reserva_por_horas_un_dia`).
- **Como mucho 7 días** (`MAX_DIAS_RESERVA` en `reservas/entity.py` y `CHECK ck_reserva_max_dias`): cubre viajes y préstamos de una semana sin que una sola petición bloquee un recurso durante meses.
- **El solapamiento entre fechas** se comprueba con los rangos: una activa ocupa algún día de `[desde, hasta]` si `fecha <= hasta` y `fecha_fin >= desde`. La misma condición sirve para la disponibilidad, la validación al crear y el resumen del mes.
- **La validación reutiliza la partición del día de la 0013.** Con varios días, la franja nueva es el día entero y cualquier activa del rango la solapa, así que basta con proyectarlas sobre un solo día: sin aforo compartido el resultado es el mismo que comprobar día a día. El aforo compartido solo existe en las salas, que se reservan por horas y de un día.
- **La disponibilidad admite un rango** (`?fecha=&fecha_fin=`) para día completo: las reservas activas del rango y si está libre entero, con y sin pendientes, y `fecha_fin` en `DisponibilidadRespuesta`. Sin franjas, que son de un solo día. Una sala, que solo se reserva por horas, no admite rango (400).
- **El resumen del mes cuenta cada reserva en cada uno de sus días**, recortada al mes.
- **Los plazos se cuentan desde el primer día** (concepto «Inicio»): cancelar, transferir y aprobar dependen de las 00:00 de `fecha`.

## Alternativas descartadas
- Un grupo de reservas de un día unidas por un identificador: varias aprobaciones o una lógica de grupo para aprobar, rechazar, cancelar y transferir a la vez; una sola fila con un rango lo resuelve sin tablas nuevas.
- Rangos también por horas (del lunes 18:00 al martes 10:00): el enunciado ata las horas a «un dia concret», y partiría la franja entre días.
- Sin tope de días: la aprobación del responsable sería el único freno.
- Un tipo `DATERANGE` de PostgreSQL: más expresivo, pero dos columnas `DATE` se leen igual de bien en Python y en la API, y las consultas solo necesitan el solape.

## Consecuencias
- Una reserva de varios días que ya ha empezado no se puede cancelar ni transferir, aunque le queden días: los plazos miran su inicio.
- Un responsable que reserva sobre una pendiente de varios días la rechaza entera, aunque solo coincidan en un día.
- En el frontend, el modal de día completo elige el último día (hasta 7) y pide la disponibilidad del rango; la URL lo guarda en `?hasta=` (decisión 0009).
