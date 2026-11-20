# Prova tècnica - Raúl

## Modelos de datos
- Reservas
  - Recurso
  - Fecha
  - ?Hora inicio
  - ?Hora fin
  - Titular (usuario)
  - ?Cantidad (aforo compartido)
  - Estado: Pendiente / Aprobada / Cancelada
  - ?Aprobada por

- Recursos
  - Nombre
  - Descripción
  - Imagen del tipo
  - Política de cancelación: Flexible / Moderada / Bloqueada
  - Tipo de reserva: Por horas / Por días
  - Tipos:
    - Salas de reunión
      - (Reservas por horas)
      - Capacidad máxima
      - Posibilidad de aforo compartido
    - Vehículos
      - (Reservas por dias completos)
      - Matrícula
      - Plazas
    - Equipo
      - (Reservas por horas)
      - (Reservas por dias completos)
      - Número de serie

- Usuairios
  - Nombre
  - Apellidos
  - Rol: Trabajador / Responsable


## Decisiones
- ~~Una reserva pendiente bloquea el recurso para todos, también para un responsable.~~
  ~~Si un responsable quiere ese hueco: primero rechaza la pendiente, luego reserva.~~
  Corregido al releer el enunciado (punto 4): un responsable puede reservar aunque haya pendientes; las que estorban se rechazan (regla 8, decisión 0016).
- Nuevo estado: Rechazada (un responsable rechaza una reserva pendiente).
- Una reserva ocupa un único día (también los vehículos).
- La disponibilidad por horas se calcula sobre el día entero, sin horario laboral: de 00:00 a 23:59, la hora de fin máxima de una reserva por horas. El día completo ocupa de 00:00 a 24:00.
- Política de cancelación (libre por cada recurso, independientemente del tipo):
  - Flexible: cancelar hasta 1h antes; transferir hasta el inicio.
  - Moderada: hasta 24h antes solo cancelar; pasado ese límite solo transferir (hasta el inicio).
  - Bloqueada: ni cancelar ni transferir.
  - Una reserva que ya ha comenzado no se puede transferir.
- Sin login: el usuario actual se carga directamente en el frontend, para poder cambiar de rol fácilmente.
- Se desarrollan las dos partes: backend (API + BD) y frontend (consume la API real).
- Asistentes de sala (`asistentes_sala`, opcional): solo se informa en salas con aforo compartido; en el resto de recursos va vacío, porque la reserva ocupa el recurso entero.

## Datos relevantes
### Tipos de recurso
Reglas fijas de cada tipo (constantes en el código, no datos guardados):
- Sala de reunión: reservas por horas · imagen `sala.png`
- Vehículo: reservas por día completo · imagen `vehiculo.png`
- Equipo: reservas por horas o por día completo · imagen `equipo.png`

### Reservas
- No se puede reservar un recurso si ya tiene una reserva

### Aprobacion de reservas
- Reserva de trabajador debe ser aprobada por responsable
- Reserva de responsable se aprueba automáticamente

### Cancelacion de reservas
- Flexible
- Moderada
- Bloqueada

## Casos de uso
- Como trabajador, quiero poder consultar los recursos diferenciados por tipo
--> 0,5h
- Como trabajador, quiero poder consultar la disponibilidad de los recursos
   - Reserva por dias: Quiero saber si está disponible en una fecha específica
   - Reserva por horas: Quiero saber si está disponible en un rango de horas específico
   - Aforo compartido: Quiero saber qué capacidad le queda libre
--> 1h
Nota: banner de disponibilidad en el momento, solo para salas
- Como trabajador, quiero saber por qué un recurso no está disponible
  - Ya reservado (ver reservas)
--> 0,25h
- Como trabajador, quiero poder hacer una reserva en un recurso
  - La reserva deberá ser aprobada por un responsable
--> 0,5h
- Como responsable, quiero poder hacer una reserva en un recurso
0h
- Como responsable, quiero poder aprobar las reservas de los trabajadores
--> 0,5h
- Como trabajador, quiero poder cancelar una reserva
  - Ver `Cancelacion de reservas`
- Como trabajador, quiero poder transferir una reserva
  - Ver `Cancelacion de reservas`
--> 0,5h

3:25h


- Usabilidad
- Recurso queda bloqueado desde que lo pido
- Podemos mockear 100% el back

## Endpoints
- GET Resorces ? Type
- GET Disponibilidad recurso ? Fecha
- POST Reserva
- PUT Cancelación
- PUT Transferir
- PUT Aprobar reserva
