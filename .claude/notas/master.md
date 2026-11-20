# master · Correcciones de la revisión

Rama: master · Planes cerrados: [backend-bd-estructura](../plans/backend-bd-estructura.md), [frontend-recursos](../plans/frontend-recursos.md), [reservas](../plans/reservas.md)

## Objetivo
Repasar la aplicación contra el enunciado y corregir lo que se interpretó de otra forma (apartado «Pendiente»).

## Hecho
- **Backend** (plan `backend-bd-estructura`): capas controller → service → repository (0001), PostgreSQL en Docker Compose (0007), entidades `Usuario`, `Recurso` (tabla única) y `Reserva` con `CHECK` con nombre, `GET /usuarios` y `GET /recursos?tipo=`.
- **Frontend** (plan `frontend-recursos`): listado `/recursos` con filtro por tipo en la URL, decisiones 0008 a 0010 y modo estricto.
- **Reservas de punta a punta** (plan `reservas`): disponibilidad por día y por mes, crear, aprobar, rechazar, cancelar y transferir (decisiones 0011 a 0013); detalle del recurso con calendario y modal con timeline, y página «Reservas» con sus pestañas. Verificado con scripts temporales fuera del repo, `npm run build` y prueba del usuario en local.
- **Datos de prueba** con reservas aleatorias creadas con las mismas reglas que la API.
- **Documentación de arquitectura:** `docs/arquitectura.md` con los diagramas reducido y detallado, enlazada desde el README.

## Pendiente
- Correcciones de la revisión del enunciado:
  - regla 8: un responsable puede reservar aunque el recurso tenga reservas pendientes (punto 4 del enunciado);
  - no aprobar reservas pendientes que ya han empezado;
  - rutas REST: `GET /recursos/{id}`, `GET /reservas/{id}` y la disponibilidad bajo `/recursos/{id}`;
  - decisión sobre la interpretación de las políticas de cancelación.
- **Diferido de las revisiones:** el color por tipo en un solo sitio, un título de pestaña por ruta, `length=None` en `tipo_enum`, el `dict` sin tipar de `recursos/service.py`, `esActiva` que replica los estados activos, el CORS solo con `GET` y `POST` y las celdas del timeline solo con ratón.

## Siguiente paso
Plan de las correcciones de la revisión.

## Pantallas acordadas
- **Detalle del recurso:** desde la tarjeta de `/recursos`, con un calendario mensual en el centro (recuento de reservas por día, días pasados atenuados).
- **Por horas:** al elegir un día se abre un modal con el timeline de 00:00 a 24:00 (franjas ocupadas con titular y estado) y la navegación de día (anterior, siguiente y calendario desplegable). Con aforo compartido, la capacidad libre por franja.
- **Día completo:** el calendario marca cada día como libre u ocupado; al pulsar un día se confirma la reserva.
- **Equipos:** en el modal se elige primero la modalidad; en día completo, el timeline se sustituye por «todo el día».
- **Reservas:** las propias y, para un responsable, las pendientes de aprobar, en pestañas «Activas» (`PENDIENTE` y `APROBADA`), «Pasadas» (`RECHAZADA`, `CANCELADA` y fechas pasadas) y «Por aprobar» (solo el responsable). Rejilla de tarjetas; cancelar y transferir solo si las reglas 13–19 lo permiten. Sin check-in ni edición.
- **Disponibilidad:** en el módulo de reservas (`DisponibilidadService`), como en el diagrama.

## Preguntas abiertas
- Ninguna.

## Contexto útil
- **Verificación:** con un venv propio y una copia del frontend en el scratchpad (el `node_modules` del repo es el de la máquina local), y `DATABASE_URL` hacia `host.docker.internal:5432`. Ver el contexto del verificador.

## Decisiones de este trabajo
- [0001](../../docs/decisiones/0001-monolito-modular-por-capas.md) a [0010](../../docs/decisiones/0010-estilos-scss-y-variables-css.md); la [0003](../../docs/decisiones/0003-postgresql-local-create-all.md) está sustituida por la [0007](../../docs/decisiones/0007-postgresql-docker-compose.md).
