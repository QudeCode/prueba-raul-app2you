# Plan: Correcciones de la revisión contra el enunciado

Estado: aprobado · Rama: master · Nivel: completo

## Objetivo
Corregir lo que, revisado contra `docs/enunciado.md`, se interpretó de otra forma: un responsable puede reservar aunque haya pendientes (punto 4), no se aprueban pendientes que ya han empezado, las rutas de la API pasan a ser más REST y la lectura de las políticas de cancelación (punto 5) queda escrita en una decisión. Cambia el contrato entre backend y frontend: los dos lados se corrigen en cada tarea.

## Fuera de alcance
- Atributos por tipo (matrícula, plazas, número de serie): ya están hechos.
- Cambiar el comportamiento de las políticas de cancelación: la D4 solo documenta la lectura vigente.
- El resumen mensual de disponibilidad (`/disponibilidad/mes`, que pasa a `/recursos/{recurso_id}/disponibilidad/mes`): sigue contando las reservas activas, también las pendientes. Ver Riesgos.
- Expirar o rechazar automáticamente las pendientes que ya han comenzado: siguen `PENDIENTE` (y bloqueando) hasta que un responsable las rechace (regla 21).
- Pantallas que consuman `GET /recursos/{id}` y `GET /reservas/{id}`: son parte del contrato REST (Swagger y otros clientes), no hacen falta en el frontend.
- Diferidos que siguen diferidos: color por tipo en un solo sitio, título por ruta, `length=None` en `tipo_enum`, el `dict` sin tipar de `recursos/service.py`, `esActiva` que replica los estados activos, el CORS solo con `GET` y `POST` y las celdas del timeline solo con ratón.
- Tests en el repositorio (regla dura de `CLAUDE.md`).

## Decisiones
Aprobar este plan es aceptar las decisiones 0014, 0015 y 0016, que se escriben ya como `aceptada`. Las decisiones vigentes no se reescriben (skill de memoria): la 0012 solo cambia su estado, porque la 0015 sustituye la parte de la ruta de la disponibilidad; la 0013 no cambia, porque la 0016 la amplía sin contradecirla.

**D4 · Políticas de cancelación (solo documentación)**
- **Decisión nueva `0014-interpretacion-politicas-de-cancelacion.md`,** tipo «decisión». Moderada: cancelar hasta 24 h antes y transferir solo desde 24 h antes hasta el inicio («passat el límit permet ser transferida»); alternativa descartada: transferir siempre, porque el «però passat el límit» del enunciado presenta la transferencia como la salida que queda cuando ya no se puede cancelar. Flexible: transferir hasta el inicio, aunque el enunciado dice «en qualsevol moment», porque una reserva empezada ya está en uso y cambiarle el titular a mitad no tiene sentido (regla 19); alternativa descartada: transferir también durante la reserva. Consecuencia: los plazos de la regla 15 y de `puede_cancelar`/`puede_transferir` (`reservas/service.py:62-79`) ya cumplen esto; no cambia código.

**D2 · No aprobar pendientes ya iniciadas**
- **Regla nueva con el número 21,** escrita en la sección «Aprobar o rechazar» detrás de la 12. Los números son identificadores: renumerar desplazaría las reglas 13 a 20, que se citan en `reservas/service.py`, `common/errores.py`, `reservas.page.ts`, `accion-dialogo.ts`, `reservas-del-dia.ts`, `reserva.model.ts` y las decisiones 0011 a 0013. Se escribe con el delimitador `21)` para que Markdown abra una lista nueva que empieza en 21 (con `21.` seguiría la lista anterior y se vería como 13). Queda entre la 12 y la 13: el orden del fichero es por secciones, no por número.
- **409 al aprobar una reserva cuyo inicio (concepto «Inicio») ya ha llegado:** `ahora >= inicio`. Es un choque con el estado actual, como los plazos (decisión 0012). Rechazar sigue permitido.
- **Una pendiente comenzada sigue bloqueando hasta que se rechace:** sigue siendo activa, así que cuenta en `libre`, en el resumen mensual y en los conflictos de un trabajador. Se acepta; no hay expiración automática (Fuera de alcance). Lo dice la propia regla 21.
- **Función pura `comenzada(inicio, ahora) -> bool`** (`ahora >= inicio`), usada por `aprobar` y por `puede_aprobar`: el borde se escribe una vez.
- **`puede_aprobar` en `ReservaRespuesta`:** `estado == PENDIENTE and not comenzada(inicio, ahora)`, calculado en `reserva_a_respuesta` como `puede_cancelar` (decisión 0013: los plazos solo en el backend). No comprueba el rol; la pestaña «Por aprobar» ya es solo de responsables.

**D3 · Rutas más REST**
- **`GET /recursos/{recurso_id}`** en `recursos/controller.py` con `RecursoService.obtener` (existe, `recursos/service.py:24-28`). 404 si no existe.
- **`GET /reservas/{reserva_id}`** con `ReservaService.obtener(reserva_id, usuario)`: 404 si no existe; 403 si quien llama no es el titular ni un responsable (un responsable ve todas porque las aprueba). Exige `X-Usuario-Id`. Se declara **después** de `/mias` y `/pendientes`: FastAPI prueba las rutas en orden y `/reservas/mias` encajaría en `{reserva_id}` y daría 422. **El 403 no es un control de privacidad:** las reservas activas ya son visibles con todos sus datos en la disponibilidad pública (`reservas` de `DisponibilidadRespuesta`), así que en la práctica solo restringe el detalle de las rechazadas y canceladas. La 0015 lo dice así.
- **Disponibilidad bajo el recurso:** `GET /recursos/{recurso_id}/disponibilidad?fecha=` y `GET /recursos/{recurso_id}/disponibilidad/mes?anio=&mes=`. Siguen en `reservas/controller.py`, en `router_disponibilidad` con `prefix="/recursos/{recurso_id}/disponibilidad"`: la URL cuelga del recurso, pero el código sigue en el módulo de reservas y `recursos` no depende de `reservas` (decisión 0012, `docs/arquitectura.md`). Se quitan `/disponibilidad` y `/disponibilidad/mes`, sin compatibilidad: el único cliente es este frontend. `main.py` no cambia (sigue incluyendo `router_disponibilidad`).
- **Un solo sitio para el 404 de una reserva:** `_para_actualizar` pasa a ser `_obtener(reserva_id, para_actualizar: bool = False)`, que usa `obtener_para_actualizar` o `obtener` del repositorio y lanza «No existe la reserva N». Lo usan las cuatro acciones (`para_actualizar=True`) y `obtener`. Un helper con un parámetro antes que dos con el mismo 404: el mensaje se escribe una vez.
- **El detalle del recurso sigue usando el catálogo** (`RecursosService.recursos`), no `GET /recursos/{id}`: el catálogo ya está cargado y compartido con el listado (decisión 0009), son 8 recursos, y una petición más solo añadiría un estado de carga. `GET /recursos/{id}` queda para la API, como `?tipo=` en la 0009.
- **Decisión nueva `0015-rutas-rest-de-recursos-y-reservas.md`,** tipo «decisión», «Sustituye en parte a 0012 (ruta de la disponibilidad)». Recoge las tres rutas, el 403 de `GET /reservas/{id}` con su alcance real (solo restringe el detalle de las reservas no activas) y que también exige `X-Usuario-Id`. Alternativas: mantener `/disponibilidad?recurso_id=` (la disponibilidad es de un recurso, y la URL anidada lo dice); mover los endpoints a `recursos/controller.py` (haría depender `recursos` de `reservas`); `GET /reservas/{id}` sin 403 (descartado para que un trabajador no lea las reservas cerradas de otros, aunque las activas sean públicas). En la 0012 solo cambia la línea `Estado:` a «aceptada · la ruta de la disponibilidad, sustituida por 0015».

**D1 · Un responsable reserva aunque haya pendientes (regla 8)**
- **Comportamiento** (decidido por el usuario): para un responsable, solo las `APROBADA` bloquean (409); si la franja cabe contando también las pendientes, no se rechaza nada; si no, se rechazan las pendientes necesarias, la más reciente (`creada_en`, `id`) primero entre las que estorban en el momento de máxima ocupación; si ni sin pendientes cabe, 409 sin rechazar nada. Para un trabajador, nada cambia.
- **Un solo algoritmo para los dos casos, en una función pura,** `pendientes_a_rechazar`. Sin aforo compartido se trata como aforo de capacidad 1 con ocupación 1 por reserva: cualquier pendiente solapada da carga ≥ 1 en algún tramo de la franja, así que el bucle las rechaza todas, que es lo pedido. Con aforo, en cada vuelta se toma el tramo de máxima carga dentro de la franja (el primero si empatan) y se rechaza la pendiente más reciente que estorba en ese momento, hasta que quepa.
- **Las candidatas se eligen por un punto, no por el tramo:** `punto = max(t.desde, inicio)` y candidatas = pendientes restantes con `inicio_r <= punto < fin_r`. Un tramo fusionado puede estar formado por varias pendientes contiguas sin que ninguna lo cubra entero (P1 09–10 y P2 10–11 dan un tramo 09–11); por el punto siempre hay candidata, y la candidata siempre se solapa con la franja nueva, así que nunca se rechaza una pendiente contigua que no estorba.
- **`rechazadas` va en el orden en que se rechazaron.** Con aforo no coincide siempre con el orden cronológico (se rechaza primero la que estorba en el pico), así que se dice igual en el contrato, en la regla 8 y en el aviso de la página.
- **Primero la comprobación sin pendientes, después el cálculo de rechazos.** `comprobar_hueco` comprueba las reglas 5 y 6 solo con las aprobadas (409 con el mensaje de siempre); si pasa, `pendientes_a_rechazar` siempre termina con la franja libre: en el `punto`, si ninguna pendiente lo cubriera, la carga sería solo de aprobadas, que ya cabía. Así el 409 nombra solo las aprobadas que bloquean.
- **`DisponibilidadService` decide, `ReservaService` aplica:** `comprobar_hueco` devuelve la lista de pendientes a rechazar sin modificarlas; `crear` las pasa a `RECHAZADA`, guarda la nueva y confirma, todo en la misma transacción, bajo el bloqueo del recurso (decisión 0013). Las rechazadas no guardan aprobador: igual que `rechazar`.
- **Las reservas activas del día se leen con `FOR UPDATE OF reserva` al crear** (`activas_del_dia_para_actualizar`). Sin eso, un responsable que crea encima de una pendiente y otro que la aprueba a la vez acaban con dos aprobadas solapadas (el `UPDATE` a `RECHAZADA` pisaría el `APROBADA`). Con el bloqueo, `crear` espera a que `aprobar` confirme y relee la fila (`populate_existing`): la ve aprobada y responde 409. Sin interbloqueo: `crear` bloquea recurso → reservas y las acciones solo la reserva.
- **La consulta de las activas del día se escribe una vez:** un helper privado del módulo `_consulta_activas_del_dia(recurso_id, fecha) -> Select[tuple[Reserva]]` que usan `activas_del_dia` y `activas_del_dia_para_actualizar`. Se prefiere a un parámetro booleano porque el repositorio ya nombra así las variantes que bloquean (`obtener` / `obtener_para_actualizar`).
- **Respuesta de `POST /reservas`: `ReservaCreadaRespuesta(ReservaRespuesta)` con `rechazadas: list[ReservaRespuesta]`.** Al heredar, el frontend sigue leyendo la reserva igual y solo añade un campo; un sobre `{reserva, rechazadas}` rompería el contrato de todos los clientes. Lista vacía cuando no se rechaza nada (también para un trabajador).
- **Vista «sin pendientes» en la disponibilidad,** que sigue pública y sigue listando las pendientes: `FranjaRespuesta.libre_sin_pendientes` y `capacidad_libre_sin_pendientes`, y `DisponibilidadRespuesta.dia_completo_libre_sin_pendientes`. Se calculan para todos (la disponibilidad no depende de quién llama) y el frontend solo las usa para un responsable. La partición se corta con todas las reservas activas y cada tramo lleva las dos cargas; los vecinos se fusionan solo si coinciden las dos. Una sola partición: las franjas de las dos vistas tienen los mismos límites.
- **`tramos` pasa a trabajar con tuplas con nombre:** entrada `Ocupacion(inicio, fin, carga, pendiente)` y salida `Tramo(desde, hasta, carga, carga_sin_pendientes)`. Con una cuarta posición anónima, `for d, h, c in …` sería fácil de leer mal.
- **Solape en una función pura,** `solapa(inicio_a, fin_a, inicio_b, fin_b) -> bool` (`inicio_a < fin_b and inicio_b < fin_a`, concepto «Solapamiento»), junto a `franja_de`. La usan `comprobar_hueco`, `pico` y `tramos`. En el frontend, igual: `seSolapa(inicioA, finA, inicioB, finB)` extraída de `tramosQueCubre`.
- **Frontend: una función `disponibilidadPara(disponibilidad, responsable)`** en `reserva.model.ts` devuelve, para un responsable, la misma `Disponibilidad` con `libre`, `capacidad_libre` y `dia_completo_libre` sustituidos por los valores sin pendientes; para un trabajador, la original. El modal calcula esa vista una vez y se la da a `motivoNoReservable`, `ajustarSeleccion` y `Timeline`, que no cambian de firma: la diferencia por rol vive en un solo sitio.
- **Qué ve un responsable en una franja con una pendiente:** la franja se puede elegir (libre en su vista, y con aforo «N libres» descuenta solo las aprobadas), el bloque de la pendiente se sigue dibujando con su rayado y su titular, y al seleccionar una franja que no cabe con las pendientes aparece el aviso de rechazo encima del botón.
- **Aviso antes de confirmar: `pendientesQueEstorban(...)`** en `reserva.model.ts`, con la disponibilidad original. Si la selección cabe contando las pendientes, ninguna. Si no: sin aforo, las pendientes que se solapan (exactamente las que el backend rechazará); con aforo, las pendientes solapadas como candidatas, con el texto «se rechazarán las necesarias entre». No se replica el bucle con aforo en el frontend: sería una segunda implementación de la regla; la lista exacta llega en la respuesta.
- **Tras crear, las rechazadas se muestran en el aviso de la página** (`role="status"`), que es donde hoy se confirma la creación: el modal se cierra al crear, como ahora. Texto, en el orden en que se rechazaron: «Reserva creada y aprobada. Se han rechazado 2 reservas pendientes: 09:00–10:00 de Ana García; 10:00–11:00 de Luis Pérez.».
- **El modal recibe `responsable` como input** desde `RecursoDetallePage`, que inyecta `UsuariosService`: el modal sigue siendo presentacional (decisión 0008), y al cambiar de usuario con el modal abierto la vista se recalcula.
- **Decisión nueva `0016-responsable-reserva-sobre-pendientes.md`,** ADR, que amplía la 0013: regla 8 nueva, algoritmo (candidatas por punto, orden de rechazo), bloqueo de las reservas del día, respuesta con `rechazadas` y vista sin pendientes. Alternativas: rechazar todas las solapadas también con aforo (rechaza de más); rechazar primero la más antigua (la más reciente es la que menos tiempo lleva planificada); dejar las pendientes sin rechazar (al aprobarlas después se superaría la capacidad y habría que recomprobar al aprobar, contra la regla 12); calcular la vista del responsable en el frontend (duplicaría la partición); un endpoint de previsualización de rechazos (otra ruta para lo que ya dicen la vista y la respuesta).

## Contrato

### Tipos
- `ReservaRespuesta` (cambia): añade `puede_aprobar: bool` (D2) después de `puede_transferir`. `PENDIENTE` y sin comenzar en el momento de la respuesta; no comprueba el rol.
- `ReservaCreadaRespuesta` (nuevo, D1): `ReservaRespuesta` + `rechazadas: list[ReservaRespuesta]`, las pendientes que esta reserva ha rechazado, ya en `RECHAZADA`, en el orden en que se rechazaron.
- `FranjaRespuesta` (cambia, D1):
  ```json
  { "inicio": "09:00", "fin": "10:30", "libre": false, "capacidad_libre": null,
    "libre_sin_pendientes": true, "capacidad_libre_sin_pendientes": null }
  ```
  `libre_sin_pendientes` y `capacidad_libre_sin_pendientes` siguen las reglas de `libre` y `capacidad_libre` contando solo las `APROBADA`.
- `DisponibilidadRespuesta` (cambia, D1): añade `dia_completo_libre_sin_pendientes: bool | null`: `true` si no hay ninguna `APROBADA` ese día; `null` si el recurso no admite día completo. `reservas` sigue con todas las activas (pendientes incluidas, con su estado).

### Endpoints
| Método y ruta | Cabecera | Query / cuerpo | Respuesta | Errores |
|---|---|---|---|---|
| `GET /recursos/{recurso_id}` (nuevo) | — | — | `RecursoRespuesta` | 404, 422 |
| `GET /recursos/{recurso_id}/disponibilidad` (sustituye a `GET /disponibilidad`) | — | `fecha: date` | `DisponibilidadRespuesta` | 404, 422 |
| `GET /recursos/{recurso_id}/disponibilidad/mes` (sustituye a `GET /disponibilidad/mes`) | — | `anio: int (2000–2100)`, `mes: int (1–12)` | `list[DiaOcupadoRespuesta]` (sin cambios) | 404, 422 |
| `GET /reservas/{reserva_id}` (nuevo) | `X-Usuario-Id` | — | `ReservaRespuesta` | 401, 403, 404, 422 |
| `POST /reservas` (cambia la respuesta) | `X-Usuario-Id` | `ReservaPeticion` | 201 `ReservaCreadaRespuesta` | 400, 401, 404, 409, 422 |
| `POST /reservas/{reserva_id}/aprobar` (nuevo 409) | `X-Usuario-Id` | — | `ReservaRespuesta` | 401, 403, 404, 409, 422 |

El resto de endpoints no cambia.

Mensajes nuevos:
- aprobar una reserva comenzada: «No se puede aprobar una reserva que ya ha comenzado».
- `GET /reservas/{id}` ajena para un trabajador: «Solo el titular o un responsable pueden ver la reserva».
- responsable con aforo, sin cabida ni sin pendientes: «Se superaría la capacidad de 10: en el momento de más ocupación ya hay 8 asistentes en reservas aprobadas». Sin aforo, el mensaje de siempre («La franja se solapa con: … (aprobada)»), que solo nombrará aprobadas.

### Frontend (`reserva.model.ts`)
- `Reserva`: `puede_aprobar: boolean`.
- `ReservaCreada extends Reserva { rechazadas: Reserva[] }`.
- `Franja`: `libre_sin_pendientes: boolean`, `capacidad_libre_sin_pendientes: number | null`.
- `Disponibilidad`: `dia_completo_libre_sin_pendientes: boolean | null`.

## Cambios

### D4 · Documentación
| Fichero | Cambio |
|---|---|
| `docs/decisiones/0014-interpretacion-politicas-de-cancelacion.md` (nuevo) | Formato de la 0012: `Estado: aceptada`, `Tipo: decisión`, Contexto (cita literal del punto 5 del enunciado), Decisión, Alternativas descartadas y Consecuencias, con el contenido de D4 en Decisiones. Remite a las reglas 15 y 19 |
| `docs/decisiones/README.md` | Fila 0014: «Interpretación de las políticas de cancelación» · aceptada |

### D2 · No aprobar pendientes iniciadas
| Fichero | Cambio | Reutiliza |
|---|---|---|
| `src/backend/app/reservas/service.py` | `comenzada(inicio, ahora) -> bool` junto a `puede_transferir`. `reserva_a_respuesta`: `puede_aprobar=reserva.estado == EstadoReserva.PENDIENTE and not comenzada(inicio, ahora)`. `aprobar`: tras `_exigir_pendiente_y_responsable`, `if comenzada(inicio_de(reserva.fecha, reserva.hora_inicio), self.reloj()): raise Conflicto("No se puede aprobar una reserva que ya ha comenzado")`. Docstring de `aprobar`: «Reglas 9, 10, 12 y 21» | `inicio_de` (`service.py:57-59`), `reserva_a_respuesta` (`service.py:94-113`) |
| `src/backend/app/reservas/dto.py` | `puede_aprobar: bool` en `ReservaRespuesta`, después de `puede_transferir`; el comentario de la línea 37 pasa a cubrir los tres | `dto.py:37-39` |
| `src/frontend/src/app/reservas/reserva.model.ts` | `puede_aprobar: boolean` en `Reserva` | — |
| `src/frontend/src/app/reservas/reservas.page.ts` | `accionesDe` en «Por aprobar»: `aprobar: reserva.puede_aprobar`; el comentario cita «reglas 14 a 19 y 21» | `reservas.page.ts:111-123` |
| `docs/reglas_negocio.md` | En «Aprobar o rechazar», detrás de la 12: `21) Solo se aprueba una reserva que no ha comenzado (concepto «Inicio»). Una pendiente que ya ha comenzado solo se puede rechazar; mientras no se rechace, sigue activa y ocupando el recurso.` | — |

### D3 · Rutas REST
| Fichero | Cambio | Reutiliza |
|---|---|---|
| `src/backend/app/recursos/controller.py` | `@router.get("/{recurso_id}") def obtener(service, recurso_id: int) -> RecursoRespuesta` | `RecursoService.obtener` (`recursos/service.py:24-28`) |
| `src/backend/app/reservas/controller.py` | `router_disponibilidad = APIRouter(prefix="/recursos/{recurso_id}/disponibilidad", tags=["disponibilidad"])`; `consultar(service, recurso_id: int, fecha: date)` y `resumen_mes(service, recurso_id: int, anio, mes)` mantienen sus parámetros (ahora `recurso_id` es de ruta). `@router.get("/{reserva_id}") def obtener(service, usuario, reserva_id: int) -> ReservaRespuesta`, declarado después de `pendientes` | `controller.py:22-40` |
| `src/backend/app/reservas/service.py` | `_para_actualizar` (`service.py:354-358`) pasa a `_obtener(reserva_id, para_actualizar: bool = False) -> Reserva`, con el 404 «No existe la reserva N»; las cuatro acciones llaman `_obtener(reserva_id, para_actualizar=True)`. `ReservaService.obtener(reserva_id, usuario) -> ReservaRespuesta`: `_obtener(reserva_id)`, 403 «Solo el titular o un responsable pueden ver la reserva» si `reserva.titular_id != usuario.id and usuario.rol != Rol.RESPONSABLE`, y `reserva_a_respuesta(reserva, self.reloj())` | `ReservaRepository.obtener` y `obtener_para_actualizar` (`repository.py:30-42`) |
| `src/frontend/src/app/reservas/reservas.service.ts` | `disponibilidad`: `url: \`${API_URL}/recursos/${id}/disponibilidad\``, `params: { fecha: dia }`. `mes`: `url: \`${API_URL}/recursos/${id}/disponibilidad/mes\``, `params: { anio, mes: numero }` | `reservas.service.ts:29-51` |
| `docs/decisiones/0015-rutas-rest-de-recursos-y-reservas.md` (nuevo) | Contenido de D3 en Decisiones, formato de la 0012, con «Sustituye en parte a: 0012 (ruta de la disponibilidad)». El 403 se describe como restricción del detalle de las reservas no activas, no como privacidad | — |
| `docs/decisiones/0012-api-de-reservas-y-errores.md` | Solo la línea `Estado:` → `aceptada · la ruta de la disponibilidad, sustituida por 0015` | — |
| `docs/decisiones/README.md` | Fila 0015 («Rutas REST de recursos, reservas y disponibilidad» · aceptada) y estado de la 0012 («aceptada · ruta de la disponibilidad sustituida por 0015») | — |
| `docs/arquitectura.md` | Tabla de módulos: recursos, backend `GET /recursos` y `GET /recursos/{id}`; reservas, backend `/recursos/{id}/disponibilidad` y `/reservas` («consultar, crear, ver una reserva, aprobar, rechazar, cancelar y transferir»), con enlace a la 0015 | `arquitectura.md:38-39` |
| `docs/diagramas/arquitectura.puml` | Etiqueta de `ReservasService --> ReservasController`: `HTTP /reservas\n/recursos/{id}/disponibilidad\n(X-Usuario-Id)` | `arquitectura.puml:179` |
| `README.md` | Viñeta «API»: los endpoints principales, `GET /recursos/{id}`, `GET /recursos/{id}/disponibilidad?fecha=`, `…/disponibilidad/mes?anio=&mes=` y `/reservas` (con `GET /reservas/{id}`), y que la disponibilidad es pública | `README.md:72` |

### D1 · Regla 8
| Fichero | Cambio | Reutiliza |
|---|---|---|
| `src/backend/app/reservas/repository.py` | `_consulta_activas_del_dia(recurso_id, fecha) -> Select[tuple[Reserva]]` (función privada del módulo: la consulta actual con `_con_relaciones` y `ORDEN`). `activas_del_dia` la ejecuta tal cual; `activas_del_dia_para_actualizar(recurso_id, fecha) -> list[Reserva]` le añade `.with_for_update(of=Reserva)` y `.execution_options(populate_existing=True)`. Docstring: evita que una pendiente se apruebe mientras otra reserva la rechaza (decisión 0016) | `activas_del_dia` (`repository.py:44-54`), patrón de `obtener_para_actualizar` (`repository.py:34-42`) |
| `src/backend/app/reservas/dto.py` | `FranjaRespuesta`: `libre_sin_pendientes: bool`, `capacidad_libre_sin_pendientes: int \| None`. `DisponibilidadRespuesta`: `dia_completo_libre_sin_pendientes: bool \| None`. `class ReservaCreadaRespuesta(ReservaRespuesta): rechazadas: list[ReservaRespuesta]` | `dto.py:42-54` |
| `src/backend/app/reservas/service.py` | Detalle abajo | `tramos`, `franja_de`, `ocupacion`, `capacidad_compartida` |
| `src/backend/app/reservas/controller.py` | `crear` devuelve `ReservaCreadaRespuesta` | `controller.py:53-55` |
| `src/backend/app/seed.py` | Tras cada `crear`, `for r in reserva.rechazadas: creadas[r.id] = r`. Sin esto, el bucle de aprobaciones (`seed.py:159-166`) intentaría aprobar una pendiente ya rechazada por un responsable y el seed fallaría con 409 | `seed.py:150-166` |
| `src/frontend/src/app/reservas/reserva.model.ts` | Tipos del Contrato. `seSolapa(inicioA, finA, inicioB, finB): boolean` extraída de `tramosQueCubre`, que pasa a usarla. `disponibilidadPara(d: Disponibilidad, responsable: boolean): Disponibilidad`. `pendientesQueEstorban(e: { recurso, modalidad: Modalidad, seleccion: Seleccion \| null, asistentes: number \| null, disponibilidad: Disponibilidad }): Reserva[]` (detalle abajo). `textoRechazadas(rechazadas: Reserva[]): string` | `tramosQueCubre` y `tramoLibre` (`reserva.model.ts:143-162`), `aMinutos`, `MINUTOS_DIA`, `textoHoras`, `nombreCompleto` |
| `src/frontend/src/app/reservas/reservas.service.ts` | `crear(nueva): Observable<ReservaCreada>`; `accion` pasa a `accion<T extends Reserva = Reserva>(ruta, cuerpo?): Observable<T>` con `http.post<T>` | `reservas.service.ts:79-90` |
| `src/frontend/src/app/reservas/reserva-modal/reserva-modal.ts`, `.html`, `.scss` | Input `responsable = input(false)`. `vista = computed(() => { const d = this.datos(); return d && disponibilidadPara(d, this.responsable()); })`. `motivo` y `elegirCelda` usan `vista()` en lugar de `datos()`; la plantilla usa `vista` (`@let`) para el `Timeline` y el bloque «Todo el día». `estorban = computed(...)`: `[]` si no es responsable, si hay `motivo()` o sin datos; si no, `pendientesQueEstorban` con `datos()` (la original). Encima del botón, si hay alguna, un bloque `.rechazos` (`role="status"`, colores `--color-pendiente`): sin aforo «Al confirmar se rechazarán estas reservas pendientes:»; con aforo «Al confirmar se rechazarán las reservas pendientes necesarias entre:»; y la lista con `ReservasDelDia` | `reserva-modal.ts:67-123`, `ReservasDelDia` |
| `src/frontend/src/app/reservas/timeline/timeline.ts` | Sin cambios: recibe las franjas de la vista, así que lo que dibuja como libre (y «N libres» con aforo) es lo que el usuario actual puede reservar; los bloques de las pendientes siguen dibujándose con su rayado | — |
| `src/frontend/src/app/reservas/recurso-detalle.page.ts`, `.html` | Inyecta `UsuariosService`; `responsable = computed(() => esResponsable(this.usuarios.actual()))`, pasado al modal como `[responsable]`. En `reservar`, `next: (reserva: ReservaCreada)`: el aviso de siempre y, si `reserva.rechazadas.length`, se le añade `textoRechazadas(reserva.rechazadas)` | `recurso-detalle.page.ts:107-129`, `esResponsable` |
| `docs/reglas_negocio.md` | Regla 8 y regla 12 nuevas, y un punto más en la 20 (texto abajo) | — |
| `docs/apuntes.md` | Líneas 41-42 tachadas (`~~…~~`) y, debajo: «Corregido al releer el enunciado (punto 4): un responsable puede reservar aunque haya pendientes; las que estorban se rechazan (regla 8, decisión 0016).» | — |
| `docs/decisiones/0016-responsable-reserva-sobre-pendientes.md` (nuevo) | ADR con el contenido de D1 en Decisiones; Consecuencias: el calendario mensual sigue contando pendientes; con aforo el aviso del modal da candidatas y la lista exacta llega en la respuesta; crear bloquea también las reservas activas del día; un trabajador puede ver partida en dos una franja ocupada (por la fusión con las dos cargas) | — |
| `docs/decisiones/README.md` | Fila 0016: «Un responsable reserva sobre pendientes» · aceptada · ADR | — |
| `docs/arquitectura.md` | Fila «Service → Service»: crear valida el hueco con la misma partición y, para un responsable, calcula qué pendientes rechazar (0016) | `arquitectura.md:52` |

Diagramas: `modelo_recursos.puml` y `modelo_bd.puml` no cambian (no hay atributos ni estados nuevos; `puede_aprobar` y las vistas sin pendientes son de los DTO). `arquitectura.puml` no cambia en D1: no hay componentes ni dependencias nuevas.

**`reservas/service.py` en D1**
- `solapa(inicio_a: time, fin_a: time, inicio_b: time, fin_b: time) -> bool`: `inicio_a < fin_b and inicio_b < fin_a`, junto a `franja_de`.
- `class Ocupacion(NamedTuple)`: `inicio: time`, `fin: time`, `carga: int`, `pendiente: bool`.
- `class Tramo(NamedTuple)`: `desde: time`, `hasta: time`, `carga: int`, `carga_sin_pendientes: int`.
- `tramos(ocupaciones: list[Ocupacion]) -> list[Tramo]`: los mismos cortes; `carga` suma las ocupaciones que `solapa` con el tramo, `carga_sin_pendientes` solo las de `pendiente=False`; se fusionan vecinos con las dos cargas iguales.
- `ocupaciones(reservas: list[Reserva], aforo: bool) -> list[Ocupacion]`: `Ocupacion(*franja_de(r.hora_inicio, r.hora_fin), ocupacion(r, aforo), r.estado == EstadoReserva.PENDIENTE)`.
- `pico(tramos: list[Tramo], inicio: time, fin: time) -> Tramo | None`: el de mayor `carga` entre los que `solapa` con `[inicio, fin)`; el primero si empatan; `None` si no hay ninguno.
- `pendientes_a_rechazar(reservas: list[Reserva], inicio: time, fin: time, asistentes: int | None, capacidad: int | None) -> list[Reserva]`:
  ```
  aforo = capacidad is not None; tope = capacidad or 1; nueva = (asistentes or 0) if aforo else 1
  restantes = list(reservas); rechazadas = []
  repetir:
      t = pico(tramos(ocupaciones(restantes, aforo)), inicio, fin)
      si t es None o t.carga + nueva <= tope: devolver rechazadas
      punto = max(t.desde, inicio)
      candidatas = pendientes de restantes con franja (i, f) tal que i <= punto < f
      la más reciente por (creada_en, id) pasa de restantes a rechazadas (se añade al final)
  ```
  Docstring con la precondición: «la franja cabe contando solo las aprobadas de `reservas`». Con ella siempre hay candidata: en `punto` la carga supera `tope - nueva`, y si ninguna pendiente cubriera `punto` esa carga sería solo de aprobadas, que ya cabía. Cada candidata cubre `punto`, que está dentro de `[inicio, fin)`, así que se solapa con la franja nueva. Devuelve las rechazadas en el orden en que se rechazaron.
- `_tramos_del_dia(recurso, reservas) -> list[Tramo]` se conserva como envoltorio: `tramos(ocupaciones(reservas, capacidad_compartida(recurso) is not None))`. Lo usan `consultar` y `comprobar_hueco`.
- `_franja(recurso: RecursoRespuesta, tramo: Tramo) -> FranjaRespuesta`: sin aforo, `libre = tramo.carga == 0`, `libre_sin_pendientes = tramo.carga_sin_pendientes == 0` y las dos capacidades `None`; con aforo, `capacidad_libre = capacidad - tramo.carga`, `capacidad_libre_sin_pendientes = capacidad - tramo.carga_sin_pendientes`, y cada `libre*` es su capacidad `> 0`.
- `DisponibilidadService.consultar`: `[self._franja(recurso, t) for t in self._tramos_del_dia(recurso, reservas)]`; `dia_completo_libre_sin_pendientes = not any(r.estado == EstadoReserva.APROBADA for r in reservas)` si admite día completo, si no `None`.
- `DisponibilidadService.comprobar_hueco(recurso, fecha, inicio, fin, asistentes, responsable: bool) -> list[Reserva]`:
  - lee con `activas_del_dia_para_actualizar`;
  - `bloqueantes` = todas (trabajador) o solo las `APROBADA` (responsable);
  - con aforo: `maximo = pico(self._tramos_del_dia(recurso, bloqueantes), inicio, fin)`, `ocupados = maximo.carga if maximo else 0` (la partición se calcula sobre la lista ya filtrada, así que `carga` es siempre la que toca y no se mezcla con `carga_sin_pendientes`); 409 si `ocupados + (asistentes or 0) > capacidad`, y con responsable el mensaje termina en «en reservas aprobadas»;
  - sin aforo: las `bloqueantes` cuya franja `solapa` con `[inicio, fin)` dan el 409 de siempre;
  - devuelve `[]` para un trabajador y `pendientes_a_rechazar(reservas, inicio, fin, asistentes, capacidad_compartida(recurso))` para un responsable. Docstring: «Reglas 5, 6 y 8».
- `ReservaService.crear`: `responsable` se calcula antes de `comprobar_hueco`; `rechazadas = self.disponibilidad.comprobar_hueco(..., responsable)`; cada una pasa a `EstadoReserva.RECHAZADA`; `guardar(reserva)`; `confirmar()`; respuesta `ReservaCreadaRespuesta(**dict(self._releer(reserva.id)), rechazadas=[self._releer(r.id) for r in rechazadas])`, que conserva el orden de rechazo.
- `_confirmar` se parte en `repositorio.confirmar()` + `_releer(reserva_id) -> ReservaRespuesta` (`obtener` y `reserva_a_respuesta`); las acciones siguen llamando a `_confirmar`, que usa `_releer`.

**`reserva.model.ts` en D1**
- `seSolapa(inicioA, finA, inicioB, finB)`: `inicioA < finB && inicioB < finA`, en minutos; `tramosQueCubre` la usa.
- `disponibilidadPara(d, responsable)`: con `responsable`, `{ ...d, franjas: d.franjas?.map((f) => ({ ...f, libre: f.libre_sin_pendientes, capacidad_libre: f.capacidad_libre_sin_pendientes })) ?? null, dia_completo_libre: d.dia_completo_libre_sin_pendientes }`; sin él, `d`.
- `pendientesQueEstorban(e)`: pendientes de `e.disponibilidad.reservas`. Día completo: todas si `dia_completo_libre === false`, si no ninguna. Por horas, sin selección válida: ninguna; si `tramoLibre(franjas, seleccion, asistentes)` con la disponibilidad original: ninguna; si no, las pendientes con `seSolapa(aMinutos(hora_inicio), aMinutos(hora_fin), seleccion.inicio, seleccion.fin)`, o de `0` a `MINUTOS_DIA` si son de día completo.
- `textoRechazadas(rechazadas)`: «Se ha rechazado 1 reserva pendiente: …» o «Se han rechazado N reservas pendientes: …», en el orden recibido (el de rechazo), cada una «09:00–10:00 de Ana García», separadas por «; ».

**Texto de `docs/reglas_negocio.md` en D1**
- Regla 8:
  ```
  8. Un responsable puede reservar aunque haya reservas pendientes en esa franja; solo le bloquean las aprobadas (reglas 5 y 6 contando solo las `APROBADA`).
     - Si la franja cabe contando también las pendientes, no se rechaza ninguna.
     - Si no cabe, se rechazan (pasan a `RECHAZADA`) las pendientes necesarias, una a una: en el momento de máxima ocupación de la franja, la más reciente de las pendientes que lo ocupan, hasta que quepa. Sin aforo compartido, eso acaba rechazando todas las que se solapan.
     - Si no cabe ni sin las pendientes, no se reserva ni se rechaza nada.
     - La respuesta indica las pendientes rechazadas, en el orden en que se rechazaron.
  ```
- Regla 12: «Al aprobar no se vuelven a comprobar conflictos: mientras una reserva está pendiente, solo un responsable puede reservar encima (regla 8), y si estorba la rechaza al hacerlo.»
- Regla 20, punto nuevo: «Para cada franja y para el día completo, también si está libre sin contar las pendientes: lo que puede reservar un responsable (regla 8).»

## Mapa del código
- `src/backend/app/reservas/service.py:33-54`: `franja_de` y `tramos`, la partición del día (0013) que cambia de forma en D1.
- `src/backend/app/reservas/service.py:57-79`: `inicio_de`, `puede_cancelar`, `puede_transferir`; junto a ellos va `comenzada`.
- `src/backend/app/reservas/service.py:94-113`: `reserva_a_respuesta`, donde se calcula `puede_aprobar`.
- `src/backend/app/reservas/service.py:155-229`: `consultar`, `comprobar_hueco` (hoy trata igual pendientes y aprobadas; solape inline en `206-211`, local `pico` en `196`), `_tramos_del_dia` y `_franja`.
- `src/backend/app/reservas/service.py:247-285`, `354-358` y `383-388`: `crear` (bloqueo del recurso y comprobación), `aprobar`, `_para_actualizar` y `_confirmar`.
- `src/backend/app/reservas/repository.py:30-54`: `obtener`, `obtener_para_actualizar` (patrón del bloqueo) y `activas_del_dia`.
- `src/backend/app/reservas/controller.py:21-55`: los dos routers, la disponibilidad con `recurso_id` de query y `crear`.
- `src/backend/app/reservas/dto.py:26-54`: `ReservaRespuesta`, `FranjaRespuesta`, `DisponibilidadRespuesta`.
- `src/backend/app/recursos/controller.py:9-17` y `recursos/service.py:24-28`: router de recursos y `obtener`, ya hecho.
- `src/backend/app/main.py:44-47`: los routers incluidos; no cambia.
- `src/backend/app/seed.py:150-176`: crea con el servicio y después aprueba, rechaza, cancela y transfiere sobre `creadas`.
- `src/frontend/src/app/reservas/reserva.model.ts:24-39`, `143-251`: tipos de disponibilidad, `tramosQueCubre`, `tramoLibre`, `motivoNoReservable` y `ajustarSeleccion`.
- `src/frontend/src/app/reservas/reserva-modal/reserva-modal.ts:67-123` y `.html:78-112`: `datos`, `motivo`, `elegirCelda`, el `Timeline`, «Todo el día» y el botón.
- `src/frontend/src/app/reservas/reservas.service.ts:29-51`, `79-90`: URLs de disponibilidad y `accion`.
- `src/frontend/src/app/reservas/recurso-detalle.page.ts:107-129` y `reservas.page.ts:111-123`: el aviso tras crear y las acciones de «Por aprobar».

## Datos y migraciones
- Sin cambios de esquema: no hay columnas ni estados nuevos.
- El seed cambia de resultado (con la misma semilla, algunas creaciones de responsables rechazan pendientes anteriores), pero sigue siendo determinista y no falla gracias al ajuste de `creadas`.

## Definición de hecho
Backend con un venv propio fuera del repo y `DATABASE_URL` hacia `host.docker.internal:5432`; `python -m app.seed` solo con autorización expresa en el encargo de verificación. Scripts temporales en el scratchpad.

- [x] Cada tarea: `PYTHONDONTWRITEBYTECODE=1 python -m compileall -q app`, `python -c "import app.main"` y `npm run build` sin errores en una copia del frontend (`tar --exclude=node_modules --exclude=dist --exclude=.angular` y `npm ci`).
- [x] D4: `0014` y su fila existen; ningún fichero de código cambia (`git diff --stat` solo en `docs/`).
- [x] D2:
  - un `ReservaService` con `reloj` fijo: aprobar una `PENDIENTE` cuyo inicio es `ahora` → 409 «No se puede aprobar una reserva que ya ha comenzado», y un minuto antes → `APROBADA`; rechazarla después del inicio → `RECHAZADA`;
  - `puede_aprobar` es `true` solo en pendientes no comenzadas, `false` en aprobadas, rechazadas y canceladas; `comenzada` en el borde exacto (`ahora == inicio` → `true`);
  - en `docs/reglas_negocio.md` la regla nueva está escrita como texto `21)` detrás de la 12, y las reglas 13 a 20 conservan su número (`grep -n '^1[3-9]\.\|^20\.' docs/reglas_negocio.md` las da todas, sin cambios respecto a `master`);
  - en local: en «Por aprobar», una pendiente de hoy ya empezada muestra «Rechazar» y no «Aprobar».
- [x] D3, con `curl`:
  - `GET /recursos/1` → el recurso; `GET /recursos/999` → 404;
  - `GET /recursos/{id}/disponibilidad?fecha=…` y `…/disponibilidad/mes?anio=…&mes=…` responden lo mismo que respondían las rutas antiguas para esos datos; `GET /disponibilidad?recurso_id=1&fecha=…` → 404;
  - `GET /reservas/{id}` como titular y como responsable → 200; como otro trabajador → 403; inexistente → 404; sin cabecera → 422;
  - `GET /reservas/mias` y `/reservas/pendientes` siguen respondiendo 200 (no los captura `{reserva_id}`);
  - las cuatro acciones siguen dando 404 «No existe la reserva N» con un id inexistente (tras el cambio a `_obtener`);
  - `/openapi.json` contiene las rutas nuevas y no `/disponibilidad`;
  - en local: el calendario del detalle y el modal cargan como antes.
- [x] D1, función pura `pendientes_a_rechazar` con reservas falsas (script sin base):
  - sin aforo: dos pendientes solapadas y una no solapada → se rechazan las dos solapadas;
  - con aforo 10: P1 (4 asistentes, 09:00–11:00, más antigua) y P2 (4, 10:00–12:00); nueva 10:00–11:00 con 3 → `[P2]`; con 2 → `[]`; con 9 → `[P2, P1]`;
  - pendientes contiguas del mismo tamaño, sin aforo: P1 09:00–10:00 y P2 10:00–11:00 (forman un solo tramo fusionado); nueva 10:00–10:30 → `[P2]`, sin error ni bucle infinito;
  - pendientes contiguas del mismo tamaño, con aforo 10: P1 09:00–10:00 (5) y P2 10:00–11:00 (5); nueva 10:00–10:30 con 6 → `[P2]`;
  - en los dos casos anteriores, P1 (contigua, sin solape con la franja nueva) no se rechaza;
  - orden de rechazo distinto del cronológico, con aforo 10: P_antigua 10:00–11:00 (8) y P_reciente 09:00–09:30 (4, creada después); nueva 09:00–11:00 con 7 → `[P_antigua, P_reciente]`;
  - empate de `creada_en`: decide el `id` mayor.
- [x] D1, con `curl` sobre el backend sembrado (o reservas creadas para la prueba en días sin reservas):
  - Sala Montaña: Ana crea 10:00–11:00 (`PENDIENTE`); Marta 10:30–11:30 → 201 `APROBADA` con `rechazadas` = [la de Ana]; `GET /reservas/{id de Ana}` como Ana → `RECHAZADA`;
  - Sala Montaña con una aprobada 10:00–11:00 y una pendiente 11:00–12:00: Marta 10:30–11:30 → 409 que nombra solo la aprobada, y la pendiente sigue `PENDIENTE`;
  - Luis sobre una pendiente → 409 como antes;
  - Sala Mar: los casos de aforo del script, por la API;
  - Furgoneta 1 con una pendiente de día completo: Jordi la reserva → 201 y la pendiente queda rechazada;
  - `GET /recursos/{id}/disponibilidad` del día con la pendiente: `libre=false` y `libre_sin_pendientes=true` en su franja; `dia_completo_libre=false` y `dia_completo_libre_sin_pendientes=true` en la furgoneta; con aforo, `capacidad_libre_sin_pendientes` = capacidad menos las aprobadas;
  - las franjas siguen cubriendo de 00:00 a 23:59 sin huecos.
- [x] D1, concurrencia (script temporal con dos hilos, repetido varias veces): Marta crea sobre la pendiente P mientras Jordi aprueba P. Nunca quedan dos `APROBADA` solapadas: o P acaba `APROBADA` y la creación da 409, o P acaba `RECHAZADA` y la aprobación da 409. Sin errores 500 ni interbloqueos.
- [x] D1, seed: `python -m app.seed` (autorizado) termina con su resumen.
- [x] D1, en local:
  - como Marta, en un día con una pendiente: el timeline deja elegir su franja con el bloque de la pendiente dibujado, el modal avisa de qué pendientes se rechazarán antes de confirmar y, tras crear, el aviso de la página las nombra en el orden de rechazo;
  - como Ana, el mismo día: la franja de la pendiente sigue ocupada y no hay aviso de rechazos;
  - cambiar de usuario con el modal abierto actualiza lo que se puede elegir;
  - en Sala Mar como Marta: «N libres» descuenta solo las aprobadas.
- [x] Docs: reglas 8, 12, 20 y 21; decisiones 0014 a 0016 y el índice; estado de la 0012; `apuntes.md`, `arquitectura.md`, `arquitectura.puml` y `README.md` según las tablas. Ningún documento lleva fechas.
- [x] `dev:revisar-cambios` a nivel `completo` (con `ui: true` en D2, D3 y D1) antes de cada commit, sin bloqueos.

## Riesgos
- **Candidatas por tramo fusionado (D1):** buscar la pendiente que «cubre» un tramo fusionado no encuentra ninguna con pendientes contiguas y el bucle falla. Se evita eligiendo por `punto` y se detecta con los casos de pendientes contiguas del script.
- **Pérdida de una aprobación concurrente (D1):** sin el `FOR UPDATE` de las reservas del día, aprobar y rechazar la misma pendiente a la vez deja dos aprobadas solapadas. Se mitiga con `activas_del_dia_para_actualizar` y se detecta con la prueba de dos hilos. El orden de bloqueo (crear: recurso → reservas; acciones: solo reserva) evita interbloqueos.
- **`populate_existing` olvidado:** la sesión devolvería el estado anterior de una fila ya cargada y la comprobación usaría datos viejos. Va en la misma consulta, como en `obtener_para_actualizar`.
- **Orden de rutas (D3):** `GET /reservas/{reserva_id}` antes de `/mias` rompe `mias` y `pendientes` con 422. Se detecta con el `curl` de la Definición de hecho.
- **Seed (D1):** sin actualizar `creadas` con las rechazadas, el seed falla al aprobar una reserva ya rechazada.
- **Pendientes comenzadas (D2):** una pendiente que ya ha empezado no se puede aprobar, pero sigue ocupando el recurso hasta que un responsable la rechace (para un trabajador, el hueco sigue ocupado). Se acepta: la regla 21 lo dice y la expiración automática queda fuera de alcance.
- **Calendario mensual para un responsable:** `/disponibilidad/mes` cuenta las pendientes, así que un vehículo con solo pendientes se ve «Ocupado» aunque Marta pueda reservarlo; al abrir el día, el modal sí le deja. Queda en las Consecuencias de la 0016; se acepta por mantener el resumen mensual como está.
- **Aviso con aforo:** lista candidatas, no la lista exacta. El texto lo dice («las necesarias entre») y la respuesta trae las exactas.
- **Más franjas en la disponibilidad:** al fusionar solo vecinos con las dos cargas iguales, un trabajador puede ver partida en dos una franja ocupada (una parte con pendiente y otra con aprobada) sin un motivo visible para él. El frontend ya trata listas de franjas de cualquier longitud; queda en las Consecuencias de la 0016.
- **`npm start` local:** no hace falta reiniciarlo (no hay carpetas nuevas), salvo que se quede con un error de compilación de un paso intermedio.

## Tareas
Cada tarea cierra en un commit propio, tras su verificación y su revisión; sin commit hasta que el usuario lo apruebe. En orden (D2, D3 y D1 tocan los mismos ficheros: no son paralelizables entre sí).

1. **D4 · Interpretación de las políticas.** `docs/decisiones/0014-interpretacion-politicas-de-cancelacion.md` y `docs/decisiones/README.md`. Verificación: lectura y `git diff --stat` solo en `docs/`.
2. **D2 · No aprobar pendientes iniciadas.** `reservas/service.py`, `reservas/dto.py`, `reserva.model.ts`, `reservas.page.ts` y la regla 21 en `docs/reglas_negocio.md`. Dentro de la tarea, backend y frontend son paralelizables [paralelizable]. Verificación: script con reloj fijo, `curl`, `grep` de la numeración, `npm run build` y prueba en local.
3. **D3 · Rutas REST.** `recursos/controller.py`, `reservas/controller.py`, `reservas/service.py` (`_obtener` y `obtener`), `reservas.service.ts`; docs: 0015, estado de la 0012, índice, `arquitectura.md`, `arquitectura.puml` y `README.md`. Backend y frontend [paralelizable]; los docs, tras los dos. Verificación: `curl` de las rutas nuevas y antiguas, `/openapi.json`, `npm run build` y prueba en local.
4. **D1 · Regla 8.** Backend: `repository.py`, `dto.py`, `service.py`, `controller.py` y `seed.py`. Frontend: `reserva.model.ts`, `reservas.service.ts`, `reserva-modal` (`.ts`, `.html`, `.scss`), `recurso-detalle.page` (`.ts`, `.html`). Docs: reglas 8, 12 y 20, `apuntes.md`, 0016, índice y `arquitectura.md`. Backend y frontend [paralelizable] con el Contrato fijado; los docs, tras los dos. Verificación: script de `pendientes_a_rechazar`, `curl`, prueba de dos hilos, seed autorizado, `npm run build` y prueba en local.

## Resultado
- Implementado en cuatro commits (D4, D2, D3 y D1), verificado con scripts temporales fuera del repo (casos de `pendientes_a_rechazar`, escenarios por la API, 20 rondas de crear contra aprobar en paralelo sin dos aprobadas solapadas, seed) y `npm run build`.
- `dev:revisar-cambios` a nivel completo con UI sobre el tramo entero, sin bloqueos. Aplicado dentro de los commits de su tarea: nota «Ya ha comenzado: solo se puede rechazar» en la tarjeta (D2); `rangoMinutos` compartido por el timeline y `pendientesQueEstorban`, rechazadas en una lista bajo el aviso de la página con el patrón `.rechazos` en los estilos globales, aviso previo con `aria-atomic` y enlazado al botón, y texto con aforo «las pendientes que haga falta de estas» (D1).
- Diferido: renombrar `comprobar_hueco` (ahora también devuelve las pendientes a rechazar) y construir `ReservaCreadaRespuesta` sin pasar por `dict`.
- Pendiente: las comprobaciones «en local» de D2, D3 y D1.
