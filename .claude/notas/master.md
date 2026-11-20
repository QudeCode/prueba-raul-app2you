# master · Reservas (siguiente funcionalidad)

Rama: master · Plan en curso: [reservas](../plans/reservas.md) (aprobado) · Planes cerrados: [backend-bd-estructura](../plans/backend-bd-estructura.md), [frontend-recursos](../plans/frontend-recursos.md)

## Objetivo
Implementar las reservas de punta a punta (backend y frontend): crear, aprobar, rechazar, cancelar, transferir y consultar la disponibilidad. El punto de partida es [docs/diagramas/arquitectura.puml](../../docs/diagramas/arquitectura.puml), donde lo previsto aparece como `«pendiente»`.

## Hecho
- **Backend** (plan `backend-bd-estructura`, cerrado con `dev:revisar-cambios` completo):
  - capas controller → service → repository (0001);
  - PostgreSQL en Docker Compose (0007, sustituye a la 0003);
  - entidades `Usuario`, `Recurso` (tabla única) y `Reserva`, con `CHECK` con nombre (incluido `hora_fin <= 23:59`);
  - seed con 4 usuarios y 8 recursos, sin reservas;
  - `GET /usuarios` y `GET /recursos?tipo=`.
- **Frontend** (plan `frontend-recursos`, cerrado con `dev:revisar-cambios` y UX):
  - listado `/recursos` con tarjetas;
  - filtro por tipo en la URL, con «Todos» por defecto (punto 1 del enunciado) y recuentos; el catálogo se pide una vez y se filtra en el cliente;
  - estilos tomados de app2u, con contraste AA;
  - modo estricto (`strict` y `strictTemplates`).
- **Decisiones del frontend:**
  - 0008: funcionalidades con capas ligeras, una cadena de llamadas en la que cada capa solo llama a la siguiente y un modelo compartido en `common/`;
  - 0009: estado en la URL y filtrado en el cliente;
  - 0010: SCSS con variables CSS y la referencia visual de app2u.
- **Diagrama de arquitectura** con lo implementado y lo pendiente, enlazado desde el README.

## Pendiente
- **Reservas implementadas** (plan `reservas`, tareas D1, B1–B5, F1–F5 y D2):
  - Backend verificado en el contenedor con scripts temporales (fuera del repo): seed, 9 rutas, códigos 400, 401, 403, 404, 409 y 422, aforo en el pico, preflight CORS, dos `crear` simultáneos (201 y 409) y cancelar con aprobar a la vez sin escrituras perdidas, bordes de plazos y `tramos`.
  - Frontend: `npm run build` sin errores (copia en el scratchpad). Lo hizo `dev:implementador`, con desviaciones menores del plan: `ReservasDelDia`, `textoHoras`, inputs extra y `Dialogo` que también cierra con clic en el fondo.
  - Dos rondas de `dev:revisar-cambios` en nivel completo con UI, sin bloqueos y con los hallazgos aplicados. Diferidos a propósito: `esActiva` replica los estados activos (se resolvería con un campo `activa` en la API), `ReservaModal` recibe el `httpResource`, el reloj inyectable sin uso, el CORS solo con `GET` y `POST`, y las celdas del timeline solo con ratón.
  - Falta: la prueba en el navegador local (Definición de hecho, bloque «En local»), reiniciando `npm start` por las carpetas nuevas y volviendo a ejecutar `python -m app.seed`.
- **Diferido de las revisiones:**
  - el color por tipo en un solo sitio (las reglas `[data-tipo]` ya están en `styles.scss`);
  - un título de pestaña por ruta;
  - `length=None`, que sobra en `tipo_enum`;
  - el `dict` sin tipar de `recursos/service.py`.

## Siguiente paso
Prueba del usuario en local (bloque «En local» de la Definición de hecho) y commit.

## Sin commit
- Todo el trabajo de reservas: backend, frontend, decisiones 0011 a 0013, documentación, contextos de los agentes, el plan y esta nota.

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
