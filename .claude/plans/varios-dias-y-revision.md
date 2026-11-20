# Plan: reservas de varios días, franjas con sus reservas y detalles de la revisión

Estado: aprobado · Rama: master · Nivel: completo

## Contexto
La revisión simulada de app2you dejó varios puntos. El usuario decide:
- **Tests:** no se hacen (se lo indicaron). Se queda como está.
- **Reservas de varios días:** los vehículos y los equipos en modalidad «día completo» pueden reservar varios días seguidos, **como máximo 7**. Las reservas por horas siguen siendo de un día.
- **Bloqueos por franja:** la disponibilidad dice, en cada franja, qué reservas la ocupan. El enunciado pide «quines reserves bloquegen».
- **Riesgo bajo, todo:**
  - la regla 21 está mal numerada;
  - `requirements.txt` no fija versiones;
  - el README del frontend es el que genera Angular CLI;
  - faltan interpretaciones por documentar;
  - el README no trae ejemplos de `curl`.
- **Favicon:** un SVG propio (calendario con marca de reservado) en lugar del `favicon.ico` de Angular.
- **Política bloqueada:** se mantiene que no se puede cancelar tampoco una reserva pendiente, y se documenta.

Se trabaja en `master` con commits normales, sin reescribir el historial. Cada commit necesita la aprobación del usuario. Al empezar, este plan se copia a `.claude/plans/varios-dias-y-revision.md`, que es la convención del proyecto.

---

## Commit 1 · Detalles de la revisión (riesgo bajo y favicon)

**Regla 21, que va fuera de orden**
- `docs/reglas_negocio.md`: el contenido de la regla 21 pasa a la regla 10: «Aprobar: … solo si la reserva no ha comenzado; una pendiente ya comenzada solo se puede rechazar y, mientras no se rechace, sigue ocupando el recurso». Se borra el bloque «21)».
- Referencias que se actualizan:
  - `src/backend/app/reservas/service.py:116` (docstring de `comenzada`) y `:389` (docstring de `aprobar`);
  - `src/frontend/src/app/reservas/reservas.page.ts:111`;
  - `.claude/notas/master.md`.

**`src/backend/requirements.txt`**
- Se fijan las versiones que ya funcionan en la máquina local, sacadas de los nombres `*.dist-info` de `src/backend/.venv` (solo se leen):

  ```
  fastapi==0.163.1
  uvicorn[standard]==0.54.0
  sqlalchemy==2.1.9
  psycopg[binary]==3.3.9
  pydantic==2.14.3
  pydantic-settings==2.16.3
  ```

**`src/frontend/README.md`**
- Se sustituye por uno breve en español: comandos (`npm install`, `npm start`, `npm run build`), estructura por funcionalidades con un enlace a la decisión 0008, y un enlace al README raíz.

**README raíz**
- Nuevo apartado «Probar la API con curl»:
  - Ana (id 1) crea una reserva por horas en la Sala Mar;
  - Marta (id 3) consulta `GET /reservas/pendientes` y la aprueba;
  - consulta `GET /recursos/{id}/disponibilidad?fecha=`.
- Las fechas van como `AAAA-MM-DD`, con una nota para sustituirlas por una fecha futura.

**Interpretaciones que faltaban por escribir**
- **Regla 4:** en las salas sin aforo compartido, `capacidad_maxima` es informativa. La reserva ocupa la sala entera y no se piden asistentes.
- **Regla 15 y decisión 0014:** la política se aplica igual a pendientes y aprobadas. Con la bloqueada, el titular tampoco puede retirar una pendiente: solo un responsable puede rechazarla. Va en la 0014, en «Decisión» y en «Consecuencias».
- **Fin del día a las 23:59:** ya está en la regla 2 y en la 0013. En `apuntes.md` se añade el porqué: PostgreSQL guarda `24:00`, pero Python no puede leerlo.

**Favicon**
- Nuevo `src/frontend/public/favicon.svg`: un calendario con una marca de reservado, con el color primario de `src/styles.scss`, de unos 20 trazos y con `viewBox="0 0 32 32"`.
- Se borra `public/favicon.ico`.
- `src/index.html:8` pasa a `<link rel="icon" type="image/svg+xml" href="favicon.svg">`.

---

## Commit 2 · Cada franja dice qué reservas la ocupan

**Backend (`src/backend/app/reservas/`)**
- `service.py`:
  - `Ocupacion` lleva el `id` de la reserva y `Tramo` lleva `ocupada_por: tuple[int, ...]`.
  - `tramos()` guarda los ids de las ocupaciones que cubren cada tramo. Al fusionar tramos vecinos (el criterio sigue siendo que tengan las dos cargas iguales), se unen sus ids sin repetir y en orden.
  - `ocupaciones()` pasa `r.id`.
  - `pendientes_a_rechazar` no cambia, porque sus candidatas se siguen buscando en un punto.
- `dto.py`: `FranjaRespuesta.ocupada_por: list[int]` guarda los ids de las reservas activas que ocupan la franja, pendientes incluidas. Están en `DisponibilidadRespuesta.reservas`. Una franja libre con aforo puede tener ocupantes.
- `DisponibilidadService._franja` rellena `ocupada_por`.

**Frontend (`src/frontend/src/app/reservas/`)**
- `reserva.model.ts`: `Franja.ocupada_por: number[]`.
- `pendientesQueEstorban` usa los ids de las franjas que cubre la selección (`tramosQueCubre`) en lugar de calcular el solape con `seSolapa` y `rangoMinutos`. `disponibilidadPara` conserva los ids también en la vista del responsable.
- `timeline.ts`: el texto accesible y el `title` de los segmentos ocupados nombran a sus ocupantes («Ocupada por …»), resueltos con `reservas[]`.

**Documentación**
- Regla 20: «para cada franja, las reservas que la ocupan».
- Nueva decisión `docs/decisiones/0017-franjas-con-sus-reservas.md`: la API dice los bloqueos y el cliente no cruza solapes. Se añade al índice.
- `docs/arquitectura.md`, solo si cita los campos de la franja.

---

## Commit 3 · Reservas de varios días (día completo, hasta 7)

**Modelo y base de datos**
- `reservas/entity.py`:
  - nueva columna `fecha_fin: Mapped[date]` (`fecha` es el primer día);
  - `CHECK ck_reserva_fechas_orden`: `fecha_fin >= fecha`;
  - `CHECK ck_reserva_por_horas_un_dia`: `hora_inicio IS NULL OR fecha_fin = fecha`;
  - `CHECK ck_reserva_max_dias`: `fecha_fin - fecha <= 6`.
- `common/` o `service.py`: la constante `MAX_DIAS_RESERVA = 7`.
- `dto.py`:
  - `ReservaPeticion.fecha_fin: date | None = None`: sin ella, es el mismo día;
  - `ReservaRespuesta.fecha_fin: date`.

**Repositorio (`reservas/repository.py`)**
- `_consulta_activas_del_dia(recurso_id, fecha)` pasa a `_consulta_activas_entre(recurso_id, desde, hasta)`, con el filtro `Reserva.fecha <= hasta AND Reserva.fecha_fin >= desde`.
  - `activas_del_dia(recurso_id, desde, hasta=None)` y `activas_del_dia_para_actualizar(...)` se renombran a `activas_entre` y `activas_entre_para_actualizar`.
  - El día suelto es `desde == hasta`.
- `activas_por_dia` pasa a `rangos_activos(recurso_id, desde, hasta) -> list[tuple[date, date]]`, con el mismo filtro de solape.
- `ORDEN` no cambia.

**Servicio (`reservas/service.py`)**
- `_validar`:
  - con `fecha_fin` y horas, error 400: «Las reservas por horas son de un solo día»;
  - si `fecha_fin < fecha`, error 400;
  - si son más de 7 días, error 400: «Como máximo 7 días seguidos»;
  - el resto no cambia y la regla 3 sigue mirando el inicio.
- `comprobar_hueco(recurso, fecha, fecha_fin, inicio, fin, asistentes, responsable)` lee `activas_entre_para_actualizar`. Cuando se piden varios días, la franja ocupa el día entero, así que cualquier activa del rango se solapa. El cálculo actual (`solapa`, `pico` y `pendientes_a_rechazar` con capacidad 1) da el resultado correcto sin tocarlo, porque el aforo compartido solo existe en las salas, que son por horas y de un día.
- `crear` guarda `fecha_fin = peticion.fecha_fin or peticion.fecha`.
- `DisponibilidadService.consultar(recurso_id, fecha, fecha_fin=None)`:
  - comprueba el rango con la misma validación (por horas, un solo día; 7 días como máximo);
  - `reservas` incluye las activas que se solapan con el rango;
  - `dia_completo_libre*` se calcula sobre todo el rango;
  - `franjas` solo se devuelve cuando es un solo día.
- `resumen_mes` cuenta cada reserva en cada día de su rango, recortado al mes. Se calcula en Python a partir de `rangos_activos`.
- `describir()` usa «del 3 al 5 de marzo, todo el día» cuando hay varios días.
- `reserva_a_respuesta` añade `fecha_fin`.

**Controlador (`reservas/controller.py`)**
- `consultar` acepta `fecha_fin: date | None = None`.

**Seed (`app/seed.py`)**
- `peticion_aleatoria`: en día completo, 1 de cada 3 reservas abarca de 2 a 4 días.
- `insertar_reservas_pasadas` pasa `fecha_fin=fecha`.

**Frontend (`src/frontend/src/app/reservas/`)**
- `reserva.model.ts`:
  - `Reserva.fecha_fin`, `ReservaNueva.fecha_fin` y la constante `MAX_DIAS = 7`;
  - `pestanaDe` usa `fecha_fin >= hoy`;
  - nuevo `textoFechas(reserva)`: «3 mar» o «3–5 mar».
- `recurso-detalle.page.ts`:
  - nuevo parámetro de URL `?hasta=` junto a `fecha` (decisión 0009), que se limpia al cambiar de día;
  - la disponibilidad se pide con `fecha_fin = hasta`;
  - `reservar` envía el rango.
- `reservas.service.ts`: `disponibilidad(recursoId, fecha, fechaFin?)` añade `&fecha_fin=` a la petición.
- `reserva-modal`:
  - en el caso de día completo, un selector «Hasta» con las opciones de `fecha` a `fecha + 6`, que emite `cambiarHasta`;
  - el bloque «Ocupado por», `motivoNoReservable` y `pendientesQueEstorban` funcionan igual sobre la disponibilidad del rango;
  - el título muestra el rango.
- `reserva-card.html` (fila «Fecha»), `accion-dialogo.html` (los tres textos) y `reservas-del-dia.html` muestran `textoFechas` cuando hay varios días.

**Documentación**
- `docs/reglas_negocio.md`:
  - conceptos «Franja» (en día completo, cada día del rango de 00:00 a 24:00) e «Inicio» (el primer día);
  - la regla 1 pasa a: «por horas, un solo día; día completo, de 1 a 7 días consecutivos (`fecha` a `fecha_fin`)»;
  - la regla 5 dice que el solape se comprueba en cada día del rango;
  - en la regla 20, la consulta de día completo admite un rango.
- `docs/apuntes.md`: se tacha «Una reserva ocupa un único día (también los vehículos)» y se añade la corrección, con el mismo formato que la de la regla 8.
- Nueva decisión `docs/decisiones/0018-reservas-de-varios-dias.md` (ADR, amplía la 0013):
  - un rango en una sola reserva, frente a un grupo de reservas de un día (una sola aprobación, se crea entera o no se crea);
  - el tope de 7 días;
  - el filtro de solape entre rangos;
  - la disponibilidad por rango;
  - las consecuencias: los plazos se cuentan desde el primer día, y una reserva que ya ha empezado no se cancela ni se transfiere.
- Índice de decisiones; en la 0012, una nota de que el contrato de crear añade `fecha_fin`.
- `docs/diagramas/modelo_bd.puml` (`fecha_fin : DATE`) y `modelo_recursos.puml` (`fechaFin : Date`).
- `docs/diagramas/arquitectura.puml`, si cita los métodos del repositorio.
- README, apartado «Uso»: vehículos y equipos de día completo hasta 7 días.

---

## Verificación
- **Backend:**
  - un venv propio en el scratchpad con el `requirements.txt` ya fijado (sirve también para comprobar que esas versiones se instalan);
  - `DATABASE_URL` hacia `host.docker.internal:5432`, con Docker Compose arrancado en local;
  - `python -m app.seed`;
  - `uvicorn` en otro puerto.
- **Script temporal fuera del repo** (con `curl` o `httpx`), que comprueba:
  - una reserva de 3 días crea una sola fila, y el resumen del mes cuenta los 3 días;
  - una reserva por horas de equipo en el día intermedio da 409, y el motivo nombra la reserva de varios días;
  - que un responsable reserve sobre una pendiente de varios días la rechaza;
  - 8 días dan 400, horas con `fecha_fin` dan 400 y `fecha_fin < fecha` da 400;
  - la disponibilidad de un rango devuelve `franjas: null` y `dia_completo_libre` correcto;
  - en `ocupada_por`, las franjas libres con aforo tienen ids y las fusionadas unen los suyos;
  - insertar a mano filas que incumplen los tres `CHECK` nuevos falla.
- **Frontend:** `npm run build` en una copia del frontend en el scratchpad, con su propio `npm ci`.
- **Revisión:** el workflow `dev:revisar-cambios` a nivel completo, con `ui: true`.
- **Prueba del usuario en local** (antes, `python -m app.seed`):
  - reservar la furgoneta 3 días y verlos ocupados en el calendario;
  - como Marta, reservar sobre una pendiente de varios días;
  - ver las tarjetas con el rango;
  - comprobar el favicon nuevo.
- **Commits:** los tres, en orden y con la aprobación del usuario para cada uno.
