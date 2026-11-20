# Plan: Reservas de punta a punta (backend y frontend)

Estado: aprobado · Rama: master · Nivel: completo

## Objetivo
Completar los puntos 2 a 5 del enunciado: consultar la disponibilidad (con el porqué y la capacidad libre), crear reservas, aprobarlas o rechazarlas, cancelarlas y transferirlas. Se hace de punta a punta: API en el módulo `reservas` del backend, y en el frontend las pantallas de detalle del recurso y «Reservas», con el usuario actual elegido en la cabecera (sin login). El punto de partida es lo que `docs/diagramas/arquitectura.puml` marca como `«pendiente»`.

## Fuera de alcance
- Login, contraseñas o tokens: el usuario actual es la cabecera `X-Usuario-Id` (apuntes: «Sin login»).
- Edición de reservas, check-in y reservas de varios días (regla 1).
- Paginación de listados: el volumen de la prueba no la necesita.
- Banner de «disponible ahora» de los apuntes (nota de la línea 79): no forma parte de las pantallas acordadas.
- Diferidos que siguen diferidos: el color por tipo en un solo sitio, un título por ruta dinámico, `length=None` en `tipo_enum` y el `dict` sin tipar de `recursos/service.py`. Sí entra la clase `.boton` con variantes, porque ahora hay botones de aprobar, rechazar y cancelar.
- Tests en el repositorio (regla dura de `CLAUDE.md`).

## Decisiones
Aprobar este plan es aceptar las decisiones 0011 a 0013, que se escriben ya como `aceptada`.

**API y usuario actual**
- **Usuario actual por la cabecera `X-Usuario-Id`** con una dependencia de FastAPI, `get_usuario_actual`, en `usuarios/controller.py`: identificar al usuario es cosa del módulo `usuarios` y es una pieza de la capa controller (diagrama). Sin cabecera → 422 (validación de FastAPI, como cualquier parámetro); con un id que no existe → **401** «Usuario desconocido». Un 404 se confundiría con «recurso no encontrado». El 401 sale de un error del dominio más, `NoAutenticado`, que lanza `UsuarioService.obtener_actual` y traduce el manejador único: no hay una segunda vía de traducción ni `try/except` en el controller.
- **Solo exigen la cabecera** los endpoints que dependen de quién llama: crear, las acciones, `mias` y `pendientes`. La disponibilidad es pública.
- **Acciones como `POST /reservas/{id}/<acción>`** (`aprobar`, `rechazar`, `cancelar`, `transferir`). Son transiciones de estado no idempotentes (repetirlas da 409), y `PUT` promete reemplazar el recurso de forma idempotente. Se aparta del `PUT` de los apuntes (sección «Endpoints»), que era un esbozo.
- **Disponibilidad bajo `/disponibilidad`,** con su propio router en `reservas/controller.py`: es un cálculo sobre las reservas (el diagrama la sitúa en el módulo de reservas), y así `recursos` no depende de `reservas`.
- **Un único DTO de reserva (`ReservaRespuesta`)** para todos los endpoints, que incluye el recurso como `RecursoRespuesta` (reutilizado) y el titular y el aprobador como `UsuarioRespuesta` (reutilizado). El frontend lo replica con los tipos `Recurso` y `Usuario` que ya tiene o crea, sin tipos nuevos de resumen.
- **`puede_cancelar` y `puede_transferir` los calcula el backend** en cada `ReservaRespuesta` (estado activo y plazos de las reglas 14, 15 y 19, con el reloj del servidor). Las reglas de plazos viven solo en Python; el frontend muestra los botones según esos campos y la acción sigue comprobando el titular (regla 13). Los valores son los del momento de la respuesta: si caducan con la página abierta, la acción responde 409 y el mensaje se ve.
- **La modalidad de una reserva se deduce de las horas:** con `hora_inicio` y `hora_fin`, por horas; sin ninguna, día completo; con solo una, 400 (regla 2). La tabla no tiene columna de modalidad y añadir un campo `modalidad` obligaría a validar que coincide con las horas.
- **Detalle del recurso sin `GET /recursos/{id}`:** la página lo busca en el catálogo que `RecursosService` ya pide una vez (decisión 0009).

**Errores del dominio**
- `app/common/errores.py`: `ErrorDominio(Exception)` y cinco subclases, `NoEncontrado`, `NoAutenticado`, `NoPermitido`, `ReglaIncumplida` y `Conflicto`. No saben nada de HTTP.
- **Un solo manejador** en `main.py`, `@app.exception_handler(ErrorDominio)`, con la tabla `ESTADO_HTTP = {NoEncontrado: 404, NoAutenticado: 401, NoPermitido: 403, ReglaIncumplida: 400, Conflicto: 409}` y el cuerpo `{"detail": "<mensaje>"}`, la misma forma que `HTTPException`. El frontend lee siempre `detail`.
- **Qué va en cada código:**
  - 401: `X-Usuario-Id` con un usuario que no existe;
  - 404: recurso, reserva o usuario destino que no existe;
  - 403: quien llama no tiene el rol o no es el titular (reglas 9 y 13), y `GET /reservas/pendientes` para un trabajador;
  - 400: la petición incumple una regla por sí sola: reglas 2 (modalidad y horas), 3 (pasado), 4 (asistentes, también `asistentes_sala > capacidad_maxima`) y 18 (transferir al propio titular);
  - 409: la petición choca con el estado actual: reglas 5, 6 y 8 (solapes y aforo), 9 y 13 (estado de la reserva), 15 y 19 (plazos de la política).
  - 422 (de FastAPI) queda para la forma: tipos, formato de la hora, `anio` y `mes` fuera de rango.

**Horas y disponibilidad**
- **Horas en minutos, sin segundos (regla 2):** tipo `HoraMinuto` en `app/common/horas.py`, un `Annotated[time, ...]` que rechaza segundos, microsegundos y zona horaria (422) y se serializa como `"HH:MM"`. Lo usan la petición y todas las respuestas. En la base, un `CHECK ck_reserva_horas_en_minutos` (decisión 0004: cada invariante de una fila lleva su `CHECK`).
- **El día reservable por horas va de 00:00 a 23:59** (`INICIO_DIA` y `FIN_DIA` en `app/common/horas.py`). El concepto «Franja» conserva 00:00–24:00 para el día completo, que ocupa el día entero; la franja por horas acaba como muy tarde a las 23:59 (regla 2), así que nada puede reservarse en el minuto 23:59–24:00. La disponibilidad trabaja en la ventana semiabierta `[00:00, 23:59)`, una reserva de día completo ocupa esa ventana entera y la última franja libre termina a las **23:59**. Así no aparece nunca una franja libre de un minuto «23:59–24:00» que no se podría reservar. El frontend dibuja el eje de 00:00 a 24:00 (pantalla acordada), pero las etiquetas de las franjas muestran «23:59», que es lo que se puede escribir en la hora de fin. Se aclara en los tres sitios que hablan del día: el concepto «Franja» y la regla 20 de `docs/reglas_negocio.md`, y la nota de `docs/apuntes.md:42`.
- **La disponibilidad es una partición del día en tramos** (decisión 0013): los inicios y fines de las reservas activas cortan la ventana en tramos consecutivos y cada tramo suma la ocupación de las reservas que lo cubren (1 por reserva sin aforo compartido, `asistentes_sala` con aforo). Con esa misma función se responde a la regla 20 y se validan las reglas 5 y 6 al crear: el máximo de ocupación de los tramos que cubre la franja nueva es «el momento de máxima ocupación» de la regla 6. Una sola implementación para consultar y para validar, así que no pueden discrepar.
- **Los plazos y el «ahora»** usan la hora local del servidor, sin zona (`datetime.now()`), como `fecha` y `hora_*`, que no la tienen. El backend y el navegador corren en la misma máquina. `ReservaService` recibe el reloj como dependencia (`reloj: Callable[[], datetime] = datetime.now`).
- **Reservas concurrentes serializadas por recurso** (decisión 0013): al crear, el servicio bloquea la fila del recurso con `SELECT … FOR UPDATE` antes de comprobar conflictos y la libera con el commit. Dos peticiones simultáneas sobre el mismo recurso no pueden pasar las dos la comprobación («garantir que ningú més pugui reservar»). Se descarta una restricción `EXCLUDE` de PostgreSQL porque no puede expresar el aforo compartido (regla 6).
- **Las acciones también bloquean:** aprobar, rechazar, cancelar y transferir leen la reserva con `obtener_para_actualizar(id)` (`with_for_update(of=Reserva)`, para que el `LEFT OUTER JOIN` del `joinedload` no impida el bloqueo) antes de comprobar su estado. Dos acciones simultáneas sobre la misma reserva (cancelar y aprobar, por ejemplo) se ejecutan una tras otra y la segunda ve el estado que dejó la primera (409), en lugar de que gane la última escritura.

**Reglas en el backend**
- **Regla 3 aplicada tal cual:** el inicio de la reserva (concepto «Inicio»: su `hora_inicio`, o las 00:00 en día completo) debe ser posterior a ahora. Consecuencia: un día completo para hoy ya no se puede reservar. Confirmado por el usuario.
- **Plazos (reglas 14, 15 y 19), con `inicio` el inicio de la reserva:**
  - Flexible: cancelar si `ahora <= inicio - 1 h`; transferir si `ahora < inicio`.
  - Moderada: cancelar si `ahora <= inicio - 24 h`; transferir si `inicio - 24 h < ahora < inicio`. Los dos intervalos no se pisan.
  - Bloqueada: ni cancelar ni transferir.
- **Orden de comprobación,** para que el código de error sea predecible: crear → 404 recurso, 400 reglas, bloqueo, 409 conflictos; acciones → 404 reserva (y usuario destino), 403 permiso, 400 regla 18, 409 estado, 409 plazo.
- **`GET /reservas/pendientes` devuelve todas las `PENDIENTE`,** también las de fechas pasadas: la regla 9 no las excluye.

**Seed**
- **Las reservas aleatorias se crean con `ReservaService`,** así cumplen todas las reglas sin repetirlas en el seed. `random.Random(2024)`: con la misma semilla salen las mismas decisiones, aunque las fechas se cuenten desde mañana. Los intentos que el servicio rechaza (409) se descartan.
- **Unas pocas reservas pasadas se insertan directamente,** sin el servicio (la regla 3 las rechazaría), para que «Pasadas» tenga contenido además de canceladas y rechazadas. Se construyen sin solapes (una por recurso y día) y con estados `APROBADA` y `RECHAZADA`.

**Frontend**
- **Usuario actual en `UsuariosService`,** con el id elegido guardado en `localStorage` (`reservas.usuarioId`). No es estado de la vista (decisión 0009) sino de la sesión, y tiene que sobrevivir a la navegación. Sin elección válida, se toma el primer usuario de la lista.
- **La cabecera `X-Usuario-Id` la pone `ReservasService` en cada petición, sin interceptor.** Las peticiones de `httpResource` que dependen del usuario (`mias`, `pendientes`) tienen que leer el signal del usuario para volver a pedirse al cambiar de usuario. Con un interceptor, la dependencia quedaría escondida y habría que leer el signal igualmente.
- **`App` es el contenedor del selector:** inyecta `UsuariosService` y pasa la lista y el usuario actual a `SelectorUsuario`, que es presentacional (regla de la 0008). Cambia la flecha del diagrama.
- **«Por aprobar» es una pestaña de «Reservas»** (pantallas acordadas): `AprobacionesPage` sale del diagrama y `DisponibilidadPage` pasa a ser `RecursoDetallePage`.
- **La página de detalle vive en `app/reservas/`:** usa el servicio de reservas, y `recursos` no puede depender de `reservas` (0008). La tarjeta de `recursos` solo enlaza a la URL `/recursos/:id`, que no es una dependencia de código.
- **Se amplía la 0008:** `reservas` puede usar el modelo, los servicios y los componentes presentacionales de `recursos` y `usuarios` (`RecursosService`, `RecursoCard`, `RecursoCabecera`, `UsuariosService`, `usuario.model`), nunca al revés; y `App` puede usar `usuarios`.
- **Componentes compartidos:** `common/dialogo/` envuelve el `<dialog>` nativo (lo usan `ReservaModal` y `AccionDialogo`) y `recursos/recurso-cabecera/` pinta imagen, nombre y tipo del recurso (lo usan `RecursoCard` y `ReservaCard`).
- **Estado de la vista en la URL (0009):** `/recursos/:id?mes=YYYY-MM&fecha=YYYY-MM-DD` (con `fecha`, el modal está abierto en ese día) y `/reservas?pestana=activas|pasadas|por-aprobar`.
- **Modales con `<dialog>` nativo** y `showModal()`: atrapan el foco y cierran con Escape sin librerías (0010).
- **Selección de horas:** dos `<input type="time" step="60">` («Desde» y «Hasta») son la vía principal y accesible. El timeline también permite elegir con el ratón por celdas de 30 minutos; sus celdas no reciben el foco.
- **«Pasadas»:** `RECHAZADA`, `CANCELADA` o `fecha` anterior a hoy. Una reserva de hoy sigue en «Activas» todo el día.
- **Vehículos:** al pulsar un día del calendario se abre el mismo modal en modo «todo el día», con «Confirmar reserva». Un día ocupado también se abre, para ver quién lo bloquea (punto 2 del enunciado), con el botón desactivado.
- **Calendario:** «Libre» u «Ocupado» solo en recursos que únicamente admiten día completo (vehículos); en salas y equipos, el recuento de reservas. Los días anteriores a `primerDiaElegible` (calculado por la página con `diaReservable` y la modalidad más permisiva del recurso: hoy en salas y equipos, mañana en vehículos) no se pueden elegir para reservar, pero si tienen reservas siguen abriéndose en modo consulta, para ver quién los ocupó; sin reservas, quedan desactivados.

## Contrato

### Tipos comunes
- Fechas `"YYYY-MM-DD"`; horas `"HH:MM"` (de `"00:00"` a `"23:59"`); `creada_en` en ISO 8601 con zona.
- `UsuarioRespuesta` (existe): `{id, nombre, apellidos, rol}`.
- `RecursoRespuesta` (existe): la unión por `tipo`.
- `ReservaRespuesta` (nuevo):
  ```json
  {
    "id": 12,
    "recurso": { "...": "RecursoRespuesta" },
    "titular": { "id": 1, "nombre": "Ana", "apellidos": "García", "rol": "TRABAJADOR" },
    "aprobada_por": null,
    "fecha": "2026-12-03",
    "hora_inicio": "09:00",
    "hora_fin": "10:30",
    "asistentes_sala": 3,
    "estado": "PENDIENTE",
    "creada_en": "2026-11-20T10:15:00+01:00",
    "puede_cancelar": true,
    "puede_transferir": false
  }
  ```
  `hora_inicio` y `hora_fin` son `null` en día completo; `asistentes_sala`, `null` salvo en salas con aforo compartido. `puede_cancelar` y `puede_transferir`: estado activo y dentro del plazo de la política en el momento de la respuesta (no comprueban el titular).
- Error: `{"detail": "<mensaje en español>"}` en 400, 401, 403, 404 y 409.

### Endpoints
| Método y ruta | Cabecera | Cuerpo / query | Respuesta | Errores |
|---|---|---|---|---|
| `GET /disponibilidad` | — | `recurso_id: int`, `fecha: date` | `DisponibilidadRespuesta` | 404, 422 |
| `GET /disponibilidad/mes` | — | `recurso_id: int`, `anio: int (2000–2100)`, `mes: int (1–12)` | `list[DiaOcupadoRespuesta]` | 404, 422 |
| `GET /reservas/mias` | `X-Usuario-Id` | — | `list[ReservaRespuesta]` del titular | 401, 422 |
| `GET /reservas/pendientes` | `X-Usuario-Id` | — | `list[ReservaRespuesta]` en `PENDIENTE` | 401, 403, 422 |
| `POST /reservas` | `X-Usuario-Id` | `ReservaPeticion` | 201 `ReservaRespuesta` | 400, 401, 404, 409, 422 |
| `POST /reservas/{reserva_id}/aprobar` | `X-Usuario-Id` | — | `ReservaRespuesta` | 401, 403, 404, 409, 422 |
| `POST /reservas/{reserva_id}/rechazar` | `X-Usuario-Id` | — | `ReservaRespuesta` | 401, 403, 404, 409, 422 |
| `POST /reservas/{reserva_id}/cancelar` | `X-Usuario-Id` | — | `ReservaRespuesta` | 401, 403, 404, 409, 422 |
| `POST /reservas/{reserva_id}/transferir` | `X-Usuario-Id` | `TransferenciaPeticion` | `ReservaRespuesta` | 400, 401, 403, 404, 409, 422 |

Las listas se ordenan por `fecha`, `hora_inicio` (los días completos primero, `NULLS FIRST`) e `id`.

- `ReservaPeticion`: `{recurso_id: int, fecha: date, hora_inicio: HoraMinuto | null = null, hora_fin: HoraMinuto | null = null, asistentes_sala: int | null = null}`.
- `TransferenciaPeticion`: `{nuevo_titular_id: int}`.
- `DisponibilidadRespuesta`:
  ```json
  {
    "recurso_id": 1,
    "fecha": "2026-12-03",
    "reservas": [ { "...": "ReservaRespuesta activas del día" } ],
    "franjas": [
      { "inicio": "00:00", "fin": "09:00", "libre": true,  "capacidad_libre": 10 },
      { "inicio": "09:00", "fin": "10:30", "libre": true,  "capacidad_libre": 7 },
      { "inicio": "10:30", "fin": "23:59", "libre": true,  "capacidad_libre": 10 }
    ],
    "dia_completo_libre": null
  }
  ```
  - `reservas`: las activas de ese día (regla 20, explican por qué no está libre), ordenadas.
  - `franjas`: la partición de `[00:00, 23:59)` en tramos consecutivos, con los tramos vecinos iguales fusionados. Sin aforo compartido, `libre` = ninguna reserva lo cubre y `capacidad_libre` = `null`. Con aforo, `capacidad_libre` = `capacidad_maxima` menos la suma de asistentes y `libre` = `capacidad_libre > 0`. Es `null` si el recurso no admite reservas por horas (vehículos).
  - `dia_completo_libre`: `true` si no hay ninguna reserva activa ese día. Es `null` si el recurso no admite día completo (salas).
  - No recorta el pasado: eso lo decide el frontend con la hora actual (y el backend al crear, regla 3).
- `DiaOcupadoRespuesta`: `{fecha: date, reservas: int}`, solo los días del mes con al menos una reserva activa.

### Frontend
- Rutas: `recursos` (existe), `recursos/:id` → `RecursoDetallePage` (`title: 'Recurso · Reservas'`), `reservas` → `ReservasPage` (`title: 'Reservas · Reservas'`).
- `localStorage['reservas.usuarioId']`: el id del usuario elegido.
- Cabecera de cada petición de `ReservasService` que la necesita: `X-Usuario-Id: <id>`.

## Cambios

### Backend (`src/backend/app/`)
| Fichero | Cambio | Reutiliza |
|---|---|---|
| `common/errores.py` (nuevo) | `ErrorDominio(Exception)` y las subclases `NoEncontrado`, `NoAutenticado`, `NoPermitido`, `ReglaIncumplida` y `Conflicto`. El mensaje, en español, es `str(error)` | — |
| `common/horas.py` (nuevo) | `INICIO_DIA = time(0, 0)`, `FIN_DIA = time(23, 59)`. `HoraMinuto = Annotated[time, AfterValidator(_sin_segundos), PlainSerializer(lambda h: h.strftime("%H:%M"), return_type=str)]`; `_sin_segundos` rechaza `second`, `microsecond` o `tzinfo` con «La hora va en minutos, sin segundos (HH:MM)» | — |
| `main.py` | Manejador único de `ErrorDominio` con `ESTADO_HTTP`. CORS: `allow_methods=["GET", "POST"]` y `allow_headers=["Content-Type", "X-Usuario-Id"]`; hoy solo permite `GET` sin cabeceras propias, y el preflight de un `POST` con `X-Usuario-Id` fallaría. Incluye `reservas_controller.router` y `reservas_controller.router_disponibilidad` | `main.py:11-14` |
| `usuarios/repository.py` | `obtener(usuario_id) -> Usuario \| None` con `session.get` | patrón `usuarios/repository.py:11-21` |
| `usuarios/service.py` | `obtener(usuario_id) -> UsuarioRespuesta`; `NoEncontrado("No existe el usuario {id}")` si no está. `obtener_actual(usuario_id) -> UsuarioRespuesta`: igual, pero con `NoAutenticado("Usuario desconocido: {id}")` | `UsuarioRespuesta.model_validate` (`service.py:14`) |
| `usuarios/controller.py` | `get_usuario_actual(x_usuario_id: Annotated[int, Header(alias="X-Usuario-Id")], service) -> UsuarioRespuesta`: devuelve `service.obtener_actual(x_usuario_id)`, sin `try/except`. Alias `UsuarioActual = Annotated[UsuarioRespuesta, Depends(get_usuario_actual)]` | `get_usuario_service` |
| `recursos/repository.py` | `obtener(recurso_id) -> Recurso \| None` con `session.get(Recurso, id)`, que devuelve la subclase | — |
| `recursos/service.py` | `obtener(recurso_id) -> RecursoRespuesta` (`NoEncontrado` si no está). `_a_respuesta` pasa a ser público, `a_respuesta`, porque lo usa `ReservaService` para el recurso de cada reserva | `service.py:23-45` |
| `reservas/entity.py` | `CHECK ck_reserva_horas_en_minutos`: `(hora_inicio IS NULL OR EXTRACT(SECOND FROM hora_inicio) = 0) AND (hora_fin IS NULL OR EXTRACT(SECOND FROM hora_fin) = 0)` | `entity.py:16-33` |
| `reservas/dto.py` (nuevo) | `ReservaPeticion`, `TransferenciaPeticion`, `ReservaRespuesta`, `FranjaRespuesta`, `DisponibilidadRespuesta` y `DiaOcupadoRespuesta`, según el Contrato. `asistentes_sala` de la petición sin `ge`: la regla 4 la valida el servicio (400) | `RecursoRespuesta`, `UsuarioRespuesta`, `HoraMinuto` |
| `reservas/repository.py` (nuevo) | `ReservaRepository(session)`: `obtener(id)`, `obtener_para_actualizar(id)` (`with_for_update(of=Reserva)`), `activas_del_dia(recurso_id, fecha)`, `activas_por_dia(recurso_id, desde, hasta) -> list[tuple[date, int]]` (`GROUP BY fecha`), `de_titular(usuario_id)`, `pendientes()`, `bloquear_recurso(recurso_id)` (`select(Recurso.id).where(...).with_for_update()`), `guardar(reserva)` (`add` y `flush`, para tener el `id`) y `confirmar()` (commit). Las listas cargan `recurso`, `titular` y `aprobada_por` con `joinedload` y ordenan como dice el Contrato. Proveedor `get_reserva_repository` | `get_session`, patrón de `recursos/repository.py` |
| `reservas/service.py` (nuevo) | Funciones puras del módulo y dos servicios (detalle abajo). Proveedores `get_disponibilidad_service` y `get_reserva_service` | `RecursoService`, `UsuarioService`, `EstadoReserva` |
| `reservas/controller.py` (nuevo) | `router = APIRouter(prefix="/reservas", tags=["reservas"])` con los 7 endpoints de reservas y `router_disponibilidad = APIRouter(prefix="/disponibilidad", tags=["disponibilidad"])` con los 2 de disponibilidad. `POST /reservas` con `status_code=201`. Solo importa servicios, DTO y `UsuarioActual` | patrón de `recursos/controller.py` |
| `seed.py` | `generar_reservas(session, aleatorio: random.Random) -> Counter[EstadoReserva]` y su llamada en `main()` tras el commit de usuarios y recursos (detalle en Datos) | `cargar_datos` |

**`reservas/service.py` en detalle**
- Constantes: `ESTADOS_ACTIVOS = (PENDIENTE, APROBADA)`.
- Funciones puras (sin sesión ni reloj; son la superficie que se prueba con scripts temporales):
  - `franja_de(reserva) -> tuple[time, time]`: `(hora_inicio, hora_fin)`, o `(INICIO_DIA, FIN_DIA)` en día completo;
  - `tramos(ocupaciones: list[tuple[time, time, int]]) -> list[tuple[time, time, int]]`: partición de `[INICIO_DIA, FIN_DIA)` por los puntos de corte, con la suma de ocupación de cada tramo y los vecinos iguales fusionados;
  - `inicio_de(fecha, hora_inicio) -> datetime`;
  - `puede_cancelar(politica, inicio, ahora) -> bool` y `puede_transferir(politica, inicio, ahora) -> bool`, con los plazos de las Decisiones.
- `DisponibilidadService(repositorio: ReservaRepository, recursos: RecursoService)`:
  - `consultar(recurso_id, fecha) -> DisponibilidadRespuesta`;
  - `resumen_mes(recurso_id, anio, mes) -> list[DiaOcupadoRespuesta]`;
  - `comprobar_hueco(recurso: RecursoRespuesta, fecha, inicio, fin, asistentes) -> None`: lanza `Conflicto` con las reservas que bloquean. Sin aforo: «La franja se solapa con: 09:00–10:30 de Ana García (pendiente)». Con aforo: «Se superaría la capacidad de 10: en el momento de más ocupación ya hay 8 asistentes».
  - La ocupación de cada reserva es `asistentes_sala` si la sala tiene aforo compartido, y 1 en el resto.
- `ReservaService(repositorio, recursos: RecursoService, usuarios: UsuarioService, disponibilidad: DisponibilidadService, reloj: Callable[[], datetime] = datetime.now)`:
  - `crear(peticion, usuario) -> ReservaRespuesta`: 404 del recurso; 400 por las reglas 2, 3 y 4 (modalidad según `recurso.modalidad_reserva`, horas juntas y en orden, inicio posterior a ahora, asistentes obligatorios y entre 1 y `capacidad_maxima` en salas con aforo, vacíos en el resto); `bloquear_recurso`; `comprobar_hueco` (409); estado según la regla 7; `guardar` y `confirmar`;
  - **respuesta tras confirmar:** `crear` y las cuatro acciones construyen la respuesta después de `confirmar()`, releyendo la reserva con `obtener(id)` (con `joinedload` de las relaciones) en la misma sesión. Así `creada_en`, que rellena el servidor, está cargado y no hay refrescos perezosos. Igual en el seed;
  - las cuatro acciones leen la reserva con `obtener_para_actualizar` (404 si no está) antes de cualquier otra comprobación;
  - `aprobar` y `rechazar(reserva_id, usuario)`: 403 si no es responsable; 409 si no está `PENDIENTE`. Aprobar guarda `aprobada_por_id` y no vuelve a comprobar conflictos (regla 12);
  - `cancelar(reserva_id, usuario)`: 403 si no es el titular; 409 si no está activa o fuera del plazo de cancelación;
  - `transferir(reserva_id, nuevo_titular_id, usuario)`: 404 del destino; 403 si no es el titular; 400 si el destino es el titular; 409 si no está activa o fuera del plazo. Solo cambia `titular_id` (regla 17);
  - `mias(usuario)` y `pendientes(usuario)` (403 si no es responsable);
  - `_a_respuesta(reserva)`: construye `ReservaRespuesta` con `RecursoService.a_respuesta(reserva.recurso)`, `UsuarioRespuesta.model_validate` para titular y aprobador, y `puede_cancelar` y `puede_transferir` con las funciones puras, el estado y `reloj()`. `DisponibilidadService` construye las reservas del día con la misma función (recibe el reloj del mismo modo).

### Frontend (`src/frontend/src/`)
| Fichero | Cambio | Reutiliza |
|---|---|---|
| `styles.scss` | Variables de estado con AA: `--color-pendiente` y `--color-pendiente-fondo` (ámbar), `--color-aprobada` y `--color-aprobada-fondo` (verde), `--color-ocupado` y `--color-libre`. Clases `.boton-secundario` (contorno) y `.boton-peligro` (rojo, `--color-error`) sobre el `button` global | `styles.scss:3-39`, `84-103` |
| `app/common/api.ts` | `mensajeDeError(error: unknown): string`: el `detail` si es texto; «No se pudo conectar con el backend.» con estado 0; si no, «Error inesperado (código N).» | `API_URL` |
| `app/common/dialogo/dialogo.ts`, `.html`, `.scss` (nuevo) | Presentacional: envuelve un `<dialog>` nativo. `abierto = input<boolean>()`, `titulo = input.required<string>()`, `cerrar = output()`, contenido con `<ng-content>`. Abre con `showModal()` en un `effect` sobre `viewChild` y emite `cerrar` en el evento `close` (también con Escape) | — |
| `app/common/fechas.ts` (nuevo) | Funciones puras sobre claves locales: `claveDia(d: Date)`, `deClaveDia(clave)`, `sumarDias(clave, n)`, `claveMes(clave)`, `sumarMeses(mes, n)`, `esClaveDia(valor)`, `esClaveMes(valor)`, `semanasDelMes(mes): (string \| null)[][]` (lunes primero) y `formatoDiaLargo(clave)` (`Intl`, `es-ES`) | — |
| `app/usuarios/usuario.model.ts` (nuevo) | `Usuario {id, nombre, apellidos, rol}` y `nombreCompleto(usuario)` | `Rol` de `common/enums.ts` |
| `app/usuarios/usuarios.service.ts` (nuevo) | `usuarios = httpResource<Usuario[]>(…/usuarios)`; `elegidoId` (signal, inicializado desde `localStorage`); `actual = computed(...)`: el elegido si está en la lista, si no el primero, o `null`; `actualId = computed(() => actual()?.id ?? null)`; `seleccionar(id)` guarda en el signal y en `localStorage` | patrón de `recursos.service.ts` |
| `app/usuarios/selector-usuario/selector-usuario.ts`, `.html`, `.scss` (nuevo) | Presentacional: `usuarios = input.required<Usuario[]>()`, `actualId = input<number \| null>()`, `cambiar = output<number>()`. `<label>` «Usuario» con un `<select>` (opción «Nombre Apellidos · Rol», con `ROL_LABELS`); se lee con una variable de plantilla (`#sel`) por `strictTemplates` | `ROL_LABELS` |
| `app/app.ts`, `app.html`, `app.scss` | Contenedor: inyecta `UsuariosService`. Cabecera con la marca, `<nav>` con «Recursos» y «Reservas» (`routerLinkActive` y `aria-current`) y `<app-selector-usuario>`. Mientras carga, el selector no se pinta; si falla, «Usuarios no disponibles» | `app.html:3-7` |
| `app/app.routes.ts` | `recursos/:id` y `reservas` antes de `**` | `app.routes.ts:4-8` |
| `app/recursos/recurso-cabecera/recurso-cabecera.ts`, `.html`, `.scss` (nuevo) | Presentacional: imagen del tipo, nombre y tipo del recurso, extraídos de `RecursoCard`. Inputs: `recurso` y `enlace: string \| null` (si lo hay, el nombre es un enlace que cubre la tarjeta con `::after`) | `recurso-card.html` |
| `app/recursos/recurso-card/recurso-card.html`, `.scss`, `.ts` | Usa `RecursoCabecera`. Nuevo input `enlazar = input(true)`: con `true`, el nombre enlaza a `/recursos/:id` y la tarjeta reacciona a `:hover` y `:focus-within`; el detalle la usa con `false`, para que el clic no borre `mes` ni `fecha` ni cierre el modal | `recurso-card.html:7` |
| `app/reservas/reserva.model.ts` (nuevo) | Tipos del Contrato y reglas en funciones puras (detalle abajo) | `Recurso`, `Usuario`, `common/enums.ts`, `common/fechas.ts` |
| `app/reservas/reservas.service.ts` (nuevo) | Detalle abajo | `API_URL`, `UsuariosService` |
| `app/reservas/calendario/calendario.ts`, `.html`, `.scss` (nuevo) | Presentacional. Inputs: `mes` (`'YYYY-MM'`), `conteos: Record<string, number>`, `seleccionada: string \| null`, `marcarLibre: boolean` (solo recursos de día completo únicamente), `primerDiaElegible: string`, `compacto: boolean`. Outputs: `elegir(dia)` y `cambiarMes(mes)`. Rejilla de lunes a domingo con `semanasDelMes`; cada día es un `<button>` con el número, el recuento de reservas o «Libre» / «Ocupado» según `marcarLibre`, y un `aria-label` completo («jueves, 3 de diciembre: 2 reservas»). Los días anteriores a `primerDiaElegible` se atenúan; con reservas siguen pulsables (consulta), sin reservas se desactivan | `fechas.ts` |
| `app/reservas/navegacion-dia/navegacion-dia.ts`, `.html`, `.scss` (nuevo) | Presentacional: «Día anterior» y «Día siguiente» y un botón con la fecha larga que despliega un `Calendario` compacto (`aria-expanded`). Escape cierra el desplegable sin cerrar el modal. Inputs: `fecha`, `primerDiaElegible`, `mes`, `conteos`, `marcarLibre`; outputs: `cambiarFecha`, `cambiarMes`. La página lo proyecta dentro de `ReservaModal` | `Calendario` |
| `app/reservas/timeline/timeline.ts`, `.html`, `.scss` (nuevo) | Presentacional. Inputs: `franjas: Franja[]`, `reservas: Reserva[]`, `aforo: boolean`, `seleccion: Seleccion \| null`, `primerMinuto: number`. Output: `elegirCelda(Seleccion)`. Barra de 00:00 a 24:00 (posición = minutos / 1440), marcas cada hora y etiquetas cada 3 h. Capas: el pasado de hoy atenuado; sin aforo, un bloque por reserva con titular y estado (pendiente con rayado y ámbar, aprobada en verde); con aforo, cada franja con «N libres» y la intensidad según la ocupación; la selección. 48 celdas de 30 min clicables con `aria-hidden`. Debajo, la lista accesible de las reservas del día («09:00–10:30 · Ana García · Pendiente · 3 personas»), que explica por qué no está libre | `aHora` |
| `app/reservas/reserva-modal/reserva-modal.ts`, `.html`, `.scss` (nuevo) | Usa `Dialogo`. Inputs: `recurso`, `fecha`, `ahora`, `disponibilidad` (el `HttpResourceRef`, leído solo con `hasValue()`), `enviando`, `error`. Outputs: `confirmar(ReservaNueva)` y `cerrar`. La navegación de día no pasa por el modal: la página proyecta `NavegacionDia` con `<ng-content>` y le da sus propios datos. Estado local en signals: `modalidad` (fijada si el recurso solo admite una; en equipos, `null` hasta que se elige con dos radios «Por horas» y «Día completo»), `seleccion` y `asistentes`. Contenido: título con el nombre del recurso, la navegación proyectada; en un día no reservable, solo la consulta (reservas del día) sin controles de reserva; en por horas, «Desde» y «Hasta» (`type="time"`), «Asistentes» (`type="number"`, `min=1`, `max=capacidad`) si hay aforo, y el `Timeline`; en día completo, el bloque «Todo el día» con «Libre» u «Ocupado por …». Debajo, el motivo de `motivoNoReservable` (`role="status"`), el error de la API (`role="alert"`) y «Confirmar reserva» (desactivado si hay motivo o `enviando`). Al cambiar de día se borran la selección y el error. Carga y error de la disponibilidad, con «Reintentar» | `Timeline`, `NavegacionDia`, funciones del modelo |
| `app/reservas/recurso-detalle.page.ts`, `.html`, `.scss` (nuevo) | Contenedor (detalle abajo) | `RecursosService.recursos`, `RecursoCard`, `ReservasService` |
| `app/reservas/reserva-card/reserva-card.ts`, `.html`, `.scss` (nuevo) | Presentacional. Inputs: `reserva`, `mostrarTitular: boolean`, `acciones: { cancelar: boolean; transferir: boolean; aprobar: boolean; rechazar: boolean }`. Outputs: `cancelar`, `transferir`, `aprobar`, `rechazar`. `RecursoCabecera` (imagen, nombre con enlace a `/recursos/:id?fecha=…` y tipo), estado (píldora con color), fecha larga, «09:00–10:30» o «Todo el día», asistentes, política, titular si `mostrarTitular` y «Aprobada por …». El pie solo aparece si hay alguna acción | `TIPO_RECURSO_LABELS`, `ESTADO_RESERVA_LABELS`, `POLITICA_CANCELACION_LABELS` |
| `app/reservas/accion-dialogo/accion-dialogo.ts`, `.html`, `.scss` (nuevo) | Usa `Dialogo` para confirmar una acción. Inputs: `accion: 'cancelar' \| 'transferir'`, `reserva`, `usuarios`, `enviando`, `error`. Outputs: `confirmar(nuevoTitularId: number \| null)` y `cerrar`. Cancelar: «¿Cancelar la reserva de X el …?». Transferir: `<select>` con los usuarios salvo el titular (regla 18) | `nombreCompleto` |
| `app/reservas/reservas-del-dia/reservas-del-dia.ts`, `.html`, `.scss` (nuevo; añadido al implementar) | Presentacional. Input `reservas: Reserva[]`. La lista accesible de las reservas del día («09:00–10:30 · Ana García · Pendiente · 3 personas»), que comparten `Timeline` y `ReservaModal` (también en modo consulta y en «Ocupado por …») | `textoHoras`, `nombreCompleto` |
| `app/reservas/reservas.page.ts`, `.html`, `.scss` (nuevo) | Contenedor (detalle abajo) | `ReservasService`, `UsuariosService` |

**Ajustes al implementar** (desviaciones aceptadas tras `dev:revisar-cambios`):
- La página «Mis reservas» pasa a llamarse «Reservas» (`ReservasPage`, ruta `/reservas`), a petición del usuario: muestra las propias y, para un responsable, las de otros pendientes de aprobar.
- `RecursoCabecera` recibe `parametros` (query params del enlace); `Timeline`, `capacidad` (intensidad con aforo); `ReservaCard`, `ocupada` (botones desactivados durante una acción).
- `reserva.model.ts` añade `textoHoras(reserva)` y `tieneAforo(recurso)`; `usuario.model.ts`, `esResponsable(usuario)`.
- `Dialogo` cierra también con clic en el fondo (solo si `mousedown` y `click` caen en el `<dialog>`) y trae un botón «Cerrar».
- «Rechazar» se confirma con `AccionDialogo` (acción `'rechazar'`); «Aprobar» no.

**`reserva.model.ts`**
- Tipos: `Reserva`, `Franja`, `Disponibilidad`, `DiaOcupado`, `ReservaNueva` (con `hora_inicio`, `hora_fin` y `asistentes_sala` como `string | null` y `number | null`), `Modalidad = 'POR_HORAS' | 'DIA_COMPLETO'`, `Seleccion { inicio: number; fin: number }` (minutos) y `Pestana = 'activas' | 'pasadas' | 'por-aprobar'`.
- Constantes: `FIN_DIA = 1439` (23:59, el último minuto reservable) y `MINUTOS_DIA = 1440` (ancho del eje).
- Funciones puras (sin Angular; el «ahora» siempre entra como parámetro):
  - `aMinutos(hora: string): number` y `aHora(minutos: number): string`;
  - `modalidadesDe(recurso: Recurso): Modalidad[]` (tabla «Modalidad por tipo»);
  - `esActiva(reserva)` y `pestanaDe(reserva, hoy: string): 'activas' | 'pasadas'`;
  - sin `puedeCancelar` ni `puedeTransferir`: los plazos los calcula el backend (`puede_cancelar` y `puede_transferir` de la respuesta);
  - `diaReservable(fecha, modalidad, ahora)`: por horas, `fecha >= hoy`; día completo, `fecha > hoy` (regla 3 con inicio a las 00:00);
  - `primerDiaElegible(recurso, ahora): string`: hoy si el recurso admite por horas, mañana si solo admite día completo;
  - `primerMinuto(fecha, ahora): number`: 0 en un día futuro, el minuto siguiente al actual hoy, y `MINUTOS_DIA` en un día pasado;
  - `motivoNoReservable({ recurso, modalidad, fecha, seleccion, asistentes, disponibilidad, ahora }): string | null`: el primer motivo, en este orden: modalidad sin elegir, día no reservable, sin franja elegida, fin no posterior al inicio, inicio ya pasado, asistentes fuera de 1..capacidad, franja ocupada o capacidad insuficiente según `disponibilidad.franjas`, día completo ocupado. `null` si se puede reservar;
  - `ajustarSeleccion(actual, celda, franjas, asistentes, primerMinuto): Seleccion | null`: sin selección, la celda; con selección, la unión de las dos si toda ella está libre; si no, la celda sola si está libre; si tampoco, `null`. El `fin` se recorta a `FIN_DIA`: la última celda (23:30–24:00) se toma como 23:30–23:59 y cuenta como libre si la franja libre llega a las 23:59. Así la API nunca recibe «24:00».

**`reservas.service.ts`** (`providedIn: 'root'`)
- `disponibilidad(recursoId: Signal<number | null>, fecha: Signal<string | null>)` → `httpResource<Disponibilidad>` (`undefined` si falta alguno), y `mes(recursoId, mes: Signal<string>)` → `httpResource<DiaOcupado[]>` con `anio` y `mes`. Se llaman desde un inicializador de campo de la página, como el patrón del plan anterior.
- `mias` y `pendientes`: `httpResource<Reserva[]>` compartidos que leen `usuarios.actualId()` (y el rol, en `pendientes`, que no se pide para un trabajador) y envían `X-Usuario-Id`.
- `crear(nueva)`, `aprobar(id)`, `rechazar(id)`, `cancelar(id)` y `transferir(id, nuevoTitularId)` devuelven `Observable<Reserva>`. Todas pasan por una función privada `accion(ruta, cuerpo?)`, que hace el `HttpClient.post` con la cabecera y en el éxito (`tap`) recarga `mias` y `pendientes`. La cabecera sale de un único helper privado `cabeceras()`, que usan también los `httpResource` de `mias` y `pendientes`.

**`RecursoDetallePage`** (`recursos/:id?mes&fecha`)
- Inputs de la URL: `id`, `mes` y `fecha`. `mesActivo`: `mes` si es válido; si no, el mes de `fecha`; si no, el mes actual. `fechaActiva`: `fecha` si es válida, o `null`.
- `recurso = computed(...)`: el del catálogo con ese `id` (lectura con `hasValue()`).
- Recursos de datos: `mes(...)` y `disponibilidad(recursoId, fechaActiva)`.
- Plantilla: «← Recursos», dos columnas (la `RecursoCard` con `enlazar=false` a la izquierda y el `Calendario` en el centro, con «Elige un día para reservar»). Estados de carga, error con «Reintentar» y «No existe el recurso.».
- `primerDiaElegible` y `marcarLibre` (el recurso solo admite día completo) se calculan aquí con las funciones del modelo y se pasan al `Calendario` y a la `NavegacionDia`.
- Al elegir un día: navega con `queryParams: { fecha, mes }` y `queryParamsHandling: 'merge'`, y el modal se abre con la `NavegacionDia` proyectada dentro. Cerrar el modal quita `fecha`. Cambiar de mes solo cambia `mes`.
- Confirmar: `crear(...)`. En el éxito, cierra el modal, recarga `mes` y `disponibilidad` y muestra «Reserva creada: pendiente de aprobación» o «Reserva creada y aprobada» (`role="status"`). En el error, `mensajeDeError` en el modal y recarga `disponibilidad`, porque el día ha podido cambiar.
- `ahora`: un signal que se actualiza cada minuto (`setInterval` con `DestroyRef`), del que salen `hoy` y `primerMinuto`.

**`ReservasPage`** (`reservas?pestana`)
- `pestanaActiva`: la de la URL si existe y está permitida (`por-aprobar` solo para un responsable); si no, `activas`.
- Pestañas como enlaces con `aria-current`: «Activas (n)», «Pasadas (n)» y, para un responsable, «Por aprobar (n)».
- Listas: `activas` y `pasadas` salen de `mias` con `pestanaDe` (activas en orden ascendente, pasadas en descendente); `por-aprobar`, de `pendientes`.
- Rejilla de `ReservaCard`. Acciones: en «Activas», `cancelar` y `transferir` según `puede_cancelar` y `puede_transferir` de la respuesta (son reservas propias, así que la regla 13 ya se cumple); en «Por aprobar», `aprobar` y `rechazar`, con `mostrarTitular`. Aprobar y rechazar se ejecutan sin diálogo; cancelar y transferir abren `AccionDialogo`.
- Mensajes de resultado (`role="status"`) y de error (`role="alert"`). Estados de carga, error y vacío por pestaña («No tienes reservas activas.», «No hay reservas pasadas.», «No hay reservas por aprobar.»).

### Documentación
| Fichero | Cambio |
|---|---|
| `docs/decisiones/0011-usuario-actual-sin-login.md` (nuevo) | Decisión: cabecera `X-Usuario-Id`, dependencia `get_usuario_actual`, 401 si no existe, selector en la cabecera, `localStorage`, cabecera puesta por `ReservasService`. Alternativas: login con token (fuera del enunciado), interceptor (esconde la dependencia reactiva), usuario en la URL |
| `docs/decisiones/0012-api-de-reservas-y-errores.md` (nuevo) | Decisión: rutas de acción con `POST`, disponibilidad bajo `/disponibilidad`, DTO único, modalidad deducida de las horas, `HoraMinuto`, errores del dominio y su tabla de códigos. Alternativas: `PUT`/`PATCH` con el estado en el cuerpo, `HTTPException` en los servicios (mezcla HTTP en el dominio) |
| `docs/decisiones/0013-disponibilidad-por-tramos.md` (nuevo) | ADR: ventana `[00:00, 23:59)` (el día completo conserva 00:00–24:00), partición en tramos usada para consultar y validar, bloqueo `FOR UPDATE` del recurso al crear y de la reserva en las acciones, plazos calculados solo en el backend. Alternativas: `EXCLUDE` con rangos (no cubre el aforo), comprobar sin bloqueo (carrera), horas en minutos 0–1440 en la API (ya descartado en la 0004) |
| `docs/decisiones/README.md` | Las tres filas, con el formato de las existentes |
| `docs/decisiones/0008-estructura-y-datos-del-frontend.md` | En el árbol: `usuarios/` y `reservas/` dejan de ser «futuro», y aparecen `common/dialogo/` y `recursos/recurso-cabecera/`. Dependencias ampliadas: `reservas` puede usar el modelo, los servicios y los componentes presentacionales de `recursos` y `usuarios`, nunca al revés, y `App` puede usar `usuarios` |
| `docs/reglas_negocio.md` | Concepto «Franja»: «por horas, de `hora_inicio` a `hora_fin` (como muy tarde las 23:59); día completo, de 00:00 a 24:00 de su fecha». Regla 20: «Por horas: las franjas libres dentro del día, de 00:00 a 23:59 (la hora de fin máxima, regla 2)» |
| `docs/apuntes.md` | La nota de la línea 42 (día de 00:00 a 24:00) se alinea con el concepto: por horas hasta las 23:59 |
| `docs/diagramas/arquitectura.puml` | Sin `«pendiente»` (y sin su `skinparam`). Frontend: `RecursoDetallePage` y `ReservasPage` en lugar de `DisponibilidadPage` y `AprobacionesPage`; un componente «componentes de reservas (Calendario, NavegacionDia, Timeline, ReservaModal, ReservaCard, AccionDialogo)», `Dialogo` en `common` y `RecursoCabecera` en recursos; `App → UsuariosService : inject` y `App → SelectorUsuario : input`; `common/fechas` y `usuario.model` en el modelo. Backend: `ReservaService → DisponibilidadService`, `ReservaService → UsuarioService`, `DisponibilidadService → RecursoService`; `common/horas` en el modelo; «manejador de errores (main)» en Controller, que traduce los errores del dominio |
| `README.md` | El seed carga además reservas aleatorias de los próximos 21 días. Sección «Uso»: elegir el usuario en la cabecera (Ana y Luis son trabajadores; Marta y Jordi, responsables), reservar desde el detalle de un recurso, «Reservas» con sus pestañas. La API, en `/docs`, pide `X-Usuario-Id` en los endpoints de reservas |
| `.claude/context/implementador.md` y `revisor-ux.md` | Implementador: `common/errores.py`, `common/horas.py`, `UsuarioActual`, `fechas.ts`, `common/dialogo/` y las dependencias ampliadas de la 0008. UX: las rutas nuevas, los colores de estado y `.boton-secundario` y `.boton-peligro` |
| `.claude/context/verificador.md` y `revisor-codigo.md` | Verificador: `compileall` como comprobación mínima y la copia del frontend con `tar`. Revisor: el `::after` de la tarjeta enlazada, los componentes fuera del plan y las reglas compartidas escritas una vez por lado |
| `.claude/notas/master.md` | Funcionalidad en curso y siguiente paso |

## Mapa del código
- `src/backend/app/main.py:8-14`: la app, el CORS solo con `allow_origins` (sin métodos ni cabeceras) y los dos routers.
- `src/backend/app/database.py:20-23`: `get_session` sin commit (0002); FastAPI comparte la sesión entre dependencias de una misma petición, y en eso se apoya el bloqueo `FOR UPDATE`.
- `src/backend/app/reservas/entity.py:12-48`: la tabla `reserva` con sus `CHECK` (incluido `hora_fin <= '23:59'`) y el índice `(recurso_id, fecha)`, que sirve a `activas_del_dia` y `activas_por_dia`.
- `src/backend/app/recursos/entity.py:12-62`: herencia de tabla única; `MODALIDAD_RESERVA` por subclase (`AMBAS` en equipos).
- `src/backend/app/recursos/service.py:16-51`: `_a_respuesta` con `match` por subclase; pasa a ser público.
- `src/backend/app/recursos/dto.py:8-38`: `RecursoRespuesta`, la unión discriminada; `ReservaRespuesta` la reutiliza (la dependencia va de `reservas` a `recursos`).
- `src/backend/app/usuarios/{repository,service,controller,dto}.py`: el patrón de capas con un proveedor por capa; `UsuarioRespuesta` con `from_attributes`.
- `src/backend/app/common/enums.py:23-33`: `ModalidadReserva` y `EstadoReserva`.
- `src/backend/app/seed.py:16-88`: `cargar_datos` sin commit y `main()` con el commit; los usuarios se insertan en el orden Ana, Luis, Marta y Jordi (ids 1 a 4).
- `src/frontend/src/app/recursos/recursos.service.ts:6-13`: el catálogo compartido con `httpResource`, que reutiliza la página de detalle.
- `src/frontend/src/app/recursos/recursos.page.ts:13-52` y `.html:29-48`: el patrón de contenedor, la lectura con `hasValue()` y los estados de carga, error y vacío.
- `src/frontend/src/app/common/enums.ts:1-50`: `EstadoReserva`, `Rol` y sus etiquetas, ya preparados para las reservas.
- `src/frontend/src/app/app.config.ts:6-13`: `withComponentInputBinding` y `withFetch`.
- `src/frontend/src/styles.scss:3-39` y `84-103`: variables de diseño y el `button` global.

## Datos y migraciones
- Sin migraciones (0007): el `CHECK` nuevo entra al recrear el esquema con `python -m app.seed`, que ya borra todo.
- **`generar_reservas(session, aleatorio)`** en `seed.py`:
  - construye los servicios a mano sobre la misma sesión (`ReservaService(ReservaRepository(session), RecursoService(RecursoRepository(session)), UsuarioService(...), DisponibilidadService(...))`);
  - para cada día de mañana a 21 días después y cada recurso, con probabilidad 0,35, intenta de 1 a 3 reservas: un titular al azar; la modalidad según el tipo (en equipos, al azar); por horas, inicio a una hora en punto o y media entre las 08:00 y las 18:00 y una duración de 1 a 3 h; asistentes entre 1 y la mitad de la capacidad en salas con aforo. Descarta los `ErrorDominio`;
  - carga los 4 usuarios una vez con `UsuarioService.obtener` (para titulares y responsables, como `UsuarioRespuesta`);
  - después, sobre las `PENDIENTE` creadas: aprueba alrededor de la mitad (Marta y Jordi alternos) y rechaza una de cada cinco;
  - cancela dos y transfiere una, elegidas entre reservas activas de recursos con política Flexible (la Moderada solo deja transferir en las últimas 24 h, y según la hora no habría candidata). El nuevo titular es el primer usuario distinto del titular. Si no hay candidata, se omite sin fallar;
  - inserta directamente, sin el servicio, unas 6 reservas en los 7 días anteriores a hoy: una por recurso y día (sin solapes), en estado `APROBADA` (con aprobador) o `RECHAZADA`;
  - imprime el resumen por estado: «Datos de prueba cargados: 4 usuarios, 8 recursos y N reservas (P pendientes, A aprobadas, R rechazadas, C canceladas).».
- `main()` hace el commit de usuarios y recursos antes de `generar_reservas`, porque el servicio confirma cada reserva.

## Definición de hecho
- [ ] `python -m app.seed` termina con el resumen por estado, y en `psql` no hay ninguna reserva con un `CHECK` incumplido; las de fecha anterior a hoy son solo las insertadas directamente (`APROBADA` o `RECHAZADA`).
- [ ] En `/openapi.json` aparecen las 9 rutas del Contrato, con `X-Usuario-Id` como cabecera obligatoria en las 7 de `/reservas`.
- [ ] Con `curl` sobre el backend sembrado:
  - `GET /disponibilidad?recurso_id=<Sala Mar>&fecha=<día con reservas>`: `franjas` cubre de `"00:00"` a `"23:59"` sin huecos, con `capacidad_libre`; `dia_completo_libre` es `null`;
  - para un vehículo: `franjas` es `null` y `dia_completo_libre` coincide con que `reservas` esté vacía;
  - `GET /disponibilidad/mes?recurso_id=…&anio=…&mes=…` coincide con el recuento de `GET /disponibilidad` de esos días;
  - `POST /reservas` como Ana (id 1) en un hueco libre → 201 `PENDIENTE`; como Marta (id 3) → 201 `APROBADA` con `aprobada_por` Marta;
  - solape parcial, total y contenido sobre una sala sin aforo → 409 con las reservas que bloquean; en Sala Mar, unos asistentes que superan la capacidad en el momento de más ocupación → 409, y que solo la superarían sumando reservas que no coinciden en el tiempo → 201;
  - `"hora_inicio": "10:00:30"` → 422; horas invertidas, solo una hora, día completo en una sala, horas en un vehículo, fecha pasada, asistentes en un vehículo o sin asistentes en Sala Mar → 400;
  - sin cabecera → 422; `X-Usuario-Id: 99` → 401, con el cuerpo `{"detail": ...}` del manejador único;
  - `puede_cancelar` y `puede_transferir` de `GET /reservas/mias` coinciden con lo que responden `cancelar` y `transferir`;
  - aprobar como Ana → 403; aprobar una `APROBADA` → 409; cancelar una reserva ajena → 403; cancelar en Cámara de vídeo (bloqueada) → 409; transferir al propio titular → 400; a un usuario inexistente → 404;
  - en Moderada, a más de 24 h: cancelar → 200 y transferir → 409 (comprobado con un `ReservaService` con `reloj` fijo, en un script temporal fuera del repo).
- [ ] Las funciones puras `tramos`, `puede_cancelar` y `puede_transferir` se comprueban con un script temporal fuera del repo, en los bordes exactos (1 h, 24 h, el inicio).
- [ ] Dos `POST /reservas` simultáneos sobre el mismo hueco (script temporal con dos hilos): uno da 201 y el otro 409.
- [ ] Cancelar y aprobar a la vez la misma `PENDIENTE` (script temporal con dos hilos): una acción da 200 y la otra 409, y el estado final es el de la primera.
- [ ] `npm run build` sin errores con `strict` y `strictTemplates` (copia del frontend en el scratchpad, por el `node_modules` de la máquina local).
- [ ] Un preflight `OPTIONS /reservas` con `Origin: http://localhost:4200`, `Access-Control-Request-Method: POST` y `Access-Control-Request-Headers: content-type,x-usuario-id` devuelve los `access-control-allow-*` correspondientes.
- [ ] En local (lo comprueba el usuario):
  - el selector cambia de usuario, se recuerda al recargar, y «Por aprobar» solo aparece para Marta y Jordi;
  - desde una tarjeta de `/recursos` se abre el detalle; el calendario muestra los recuentos y atenúa los días pasados (los que tienen reservas se abren en modo consulta); en un vehículo marca «Libre» u «Ocupado» y hoy no se puede elegir para reservar; en un equipo, recuentos;
  - en el detalle, pulsar la tarjeta del recurso no cambia la URL ni cierra el modal;
  - en el timeline se puede elegir la última media hora y se reserva hasta las 23:59;
  - en Sala Mar, el modal muestra la capacidad libre por franja; en Sala Montaña, los bloques con titular y estado; la navegación de día y el calendario desplegable cambian `fecha` en la URL; recargar la página mantiene el modal abierto en ese día;
  - en un equipo, primero se elige la modalidad, y «Día completo» sustituye el timeline por «Todo el día»;
  - reservar crea la reserva y el calendario actualiza el recuento; un conflicto muestra el mensaje de la API dentro del modal;
  - en «Reservas», cancelar y transferir solo aparecen cuando las reglas 13 a 19 lo permiten, y aprobar o rechazar mueve la reserva de pestaña;
  - con el backend parado, cada vista muestra su error con «Reintentar».
- [ ] `docs/` actualizado según la tabla de Documentación; ningún documento lleva fechas; `arquitectura.puml` no contiene `pendiente`.
- [ ] `dev:revisar-cambios` a nivel `completo` con `ui: true`, sin bloqueos.

## Riesgos
- **CORS:** sin `allow_methods` ni `allow_headers`, el navegador bloquea todos los `POST` y las peticiones con `X-Usuario-Id` aunque `curl` funcione. Se detecta con el preflight de la Definición de hecho.
- **El bloqueo depende de compartir la sesión:** si `RecursoService` y `ReservaRepository` usaran sesiones distintas, `FOR UPDATE` no protegería nada. FastAPI cachea `get_session` por petición, y el seed construye los servicios con la misma sesión. Se detecta con la prueba de dos hilos.
- **Reglas duplicadas en el frontend** (modalidades, regla 3): pueden divergir del backend. Los plazos ya no se duplican (los calcula el backend). Se mitiga con los mismos nombres y bordes en los dos lados, y porque el backend es la autoridad (0008): si discrepan, la API responde 400 o 409 y el mensaje se ve.
- **Hora local:** backend y navegador deben compartir zona horaria. En local se cumple; si se despliega en otra máquina, los plazos se desplazan. Queda escrito en la 0013.
- **`value()` lanza en error (hallazgo):** todos los `httpResource` nuevos se leen con `hasValue()`, también la disponibilidad que recibe el modal.
- **`<dialog>` y Angular:** `showModal()` sobre un elemento que todavía no está en el DOM falla. `Dialogo` lo abre en un `effect` sobre `viewChild` y emite `cerrar` con el evento `close`, para que Escape también actualice la URL. Al estar en un solo componente, el patrón no se repite.
- **`npm start` local** no ve carpetas nuevas (hallazgo): reiniciarlo tras crear `usuarios/` y `reservas/`.
- **Tamaño de `reservas/service.py`:** dos servicios y las funciones puras rondan las 250 líneas. Se mantienen en un fichero por la convención de la 0001; si creciera más, las funciones puras serían lo primero en salir.

## Tareas
Con el contrato fijado en este plan, la rama de backend (B) y la de frontend (F) tocan ficheros disjuntos y avanzan en paralelo. Dentro de cada rama, el orden es el indicado.

1. **D1 · Decisiones** 0011, 0012 y 0013 y su índice. [paralelizable]
2. **B1 · Base común del backend:** `common/errores.py`, `common/horas.py` y, en `main.py`, el manejador y el CORS. [paralelizable con F]
3. **B2 · Usuarios:** `obtener` en el repository y el servicio, y `get_usuario_actual`/`UsuarioActual` en el controller. Tras B1. [paralelizable con B3]
4. **B3 · Recursos:** `obtener` en el repository y el servicio, y `a_respuesta` público. Tras B1. [paralelizable con B2]
5. **B4 · Reservas:** el `CHECK` de la entidad, `dto.py`, `repository.py`, `service.py` y `controller.py`, y los routers en `main.py`. Tras B2 y B3. Comprobar con `curl` y los scripts temporales.
6. **B5 · Seed:** `generar_reservas`. Tras B4.
7. **F1 · Base común del frontend:** `styles.scss`, `common/api.ts`, `common/fechas.ts`, `common/dialogo/`, `recursos/recurso-cabecera/` y su uso en `RecursoCard` (con el input `enlazar`), `usuarios/` (modelo, servicio y selector) y la cabecera de `App`. [paralelizable con B]
8. **F2 · Modelo y servicio de reservas:** `reserva.model.ts` y `reservas.service.ts`. Tras F1.
9. **F3 · Detalle del recurso:** `Calendario`, `NavegacionDia`, `Timeline`, `ReservaModal` y `RecursoDetallePage`. Tras F2. [paralelizable con F4]
10. **F4 · Reservas:** `ReservaCard`, `AccionDialogo` y `ReservasPage`. Tras F2. [paralelizable con F3]
11. **F5 · Rutas:** `recursos/:id` y `reservas` en `app.routes.ts`. Tras F3 y F4, que así no comparten fichero.
12. **D2 · Documentación:** `arquitectura.puml`, `reglas_negocio.md` (concepto «Franja» y regla 20), `apuntes.md`, el árbol y las dependencias de la 0008, `README.md`, el contexto del implementador y de UX, y la nota. Tras B5 y F5.
13. **Verificación de punta a punta** (Definición de hecho) y `dev:revisar-cambios` a nivel `completo` con `ui: true`. Sin commit hasta que el usuario lo apruebe.
