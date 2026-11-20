# 0014 · Interpretación de las políticas de cancelación

Estado: aceptada
Tipo: decisión

## Contexto
El enunciado (punto 5) define tres políticas:

> - **Flexible**: cancel·lació fins 1h abans i permet ser transferida a un altre usuari en qualsevol moment.
> - **Moderada**: cancel·lació fins 24h abans, però passat el límit permet ser transferida a un altre usuari.
> - **Bloquejada**: no es pot cancel·lar ni transferir a un altre usuari

La bloqueada no deja dudas. En la moderada no se dice si se puede transferir antes del límit, y en la flexible «en qualsevol moment» no aclara si incluye una reserva que ya ha empezado. Las reglas 15 y 19 recogen la lectura elegida; esta decisión explica por qué.

## Decisión
- **Moderada: cancelar hasta 24 h antes; transferir solo desde 24 h antes hasta el inicio.** El «però passat el límit» presenta la transferencia como la salida que queda cuando ya no se puede cancelar: antes del límit, quien no puede usar la reserva la cancela y libera el recurso para todos; después, ya no puede liberarlo, pero sí cedérselo a otra persona.
- **Flexible: transferir hasta el inicio.** Una reserva que ya ha empezado está en uso, y cambiarle el titular a mitad no tiene sentido (regla 19). «En qualsevol moment» se lee como «sin plazo previo», a diferencia de la moderada.
- **Los plazos se cuentan hasta el inicio de la reserva** (regla 14; en día completo, las 00:00 de su fecha).
- **La política vale igual para pendientes y aprobadas.** El enunciado no distingue: cancelar es cancelar la reserva, esté aprobada o no. Con la bloqueada, quien ha pedido una reserva no puede retirarla; si ya no la necesita, un responsable la rechaza.

## Alternativas descartadas
- Moderada con transferencia en cualquier momento hasta el inicio: deja sin sentido el «passat el límit», porque la transferencia no dependería del plazo.
- Flexible con transferencia también durante la reserva: el titular cambiaría mientras la reserva se está usando.
- Dejar retirar siempre las pendientes, sea cual sea la política: trata la pendiente como una petición y no como una reserva, una distinción que el enunciado no hace.

## Consecuencias
- No cambia código: `puede_cancelar` y `puede_transferir` (`reservas/service.py`) ya aplican estos plazos, y el frontend solo muestra lo que dicen.
- En la moderada, desde que se crea la reserva hasta 24 h antes del inicio solo se puede cancelar; en las últimas 24 h, solo transferir.
- En la bloqueada, una pendiente solo sale de «Activas» si un responsable la rechaza.
