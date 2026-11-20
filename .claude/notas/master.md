# master · Listado de recursos (frontend)

Rama: master · Plan en curso: [frontend-recursos](../plans/frontend-recursos.md) · Plan anterior, cerrado: [backend-bd-estructura](../plans/backend-bd-estructura.md)

## Objetivo
Primera funcionalidad completa de punta a punta antes de las reservas: la pantalla `/recursos` en Angular (tarjetas con filtro por tipo en la URL) sobre `GET /recursos?tipo=`, con las decisiones del frontend (0008 a 0010) y la referencia visual de app2u.

## Hecho
- Diagrama de arquitectura por capas (`docs/diagramas/arquitectura.puml`), enlazado desde el README: pila de llamadas (Presentación → Datos → HTTP → Controller → Service → Repository → BD) y el modelo de cada mitad aparte; lo previsto para reservas aparece como `«pendiente»`. La 0008 distingue la cadena de llamadas (cada capa solo llama a la siguiente) del modelo compartido.
- **Listado de recursos (plan `frontend-recursos`):** decisiones 0008 a 0010; `GET /recursos?tipo=` en el backend (parte de la API; el listado filtra en el cliente, 0009); en el frontend, `strict` + `strictTemplates`, `index.html` en español con Inter, `common/api.ts` y `common/enums.ts`, rutas, carcasa con cabecera (se retira la comprobación provisional), `recursos/` (modelo, servicio con `httpResource` que pide el catálogo una vez, página con filtro en memoria con recuentos y estados, tarjeta) y `styles.scss` con la paleta de app2u. Imágenes extraídas de los zip a `public/imagenes/recursos/`. Verificado: compila en modo estricto; el filtro devuelve 8/3/2/3 y 422 con un tipo desconocido; CORS; `ng serve` sirve la página y las imágenes; `value()` lanza en error (`ResourceValueError`). El usuario ya lo ve en local. `dev:revisar-cambios` hecho y aplicado: zip quitados por el usuario; contraste AA, `role="status"`, «Saltar al contenido», píldoras de 44 px y `prefers-reduced-motion`; Inter en Google Fonts (anotado en la 0010).
- Arquitectura del frontend documentada en la 0008 (ADR): capas, reglas de dependencia, alternativas valoradas y cómo crecer. `shared/` → `common/`, con los enums del dominio y sus etiquetas en `common/enums.ts` (más `EstadoReserva` y `Rol`). El usuario decidió mantener «Todos» (punto 1 del enunciado) y la estructura por funcionalidad.
- Modelado cerrado: diagramas de clases y BD, `docs/reglas_negocio.md` (reglas 1 a 20) y decisiones de negocio en `docs/apuntes.md`.
- Decisiones técnicas 0001 a 0007 aceptadas (`docs/decisiones/`); la 0003 está sustituida por la 0007.
- Plan aprobado y revisado por `dev:revisar-plan` a nivel completo, con sus hallazgos incorporados.
- Contexto de ai-bank: `CLAUDE.md`, `.claude/context/` (6 agentes de `dev`) y `.claude/settings.json`.
- Tarea 1 del plan: `requirements.txt` con versiones mínimas, `.env.example` y `.env` en `.gitignore`.
- Tarea 2 del plan (revisada con `dev:revisar-plan`): `app/config.py`, `app/database.py` (`get_session`, `check_enum`, `recrear_esquema`) y `app/common/enums.py`. Verificada con un script temporal fuera del repo; `recrear_esquema` y la conexión real se prueban en la tarea 3.
- Tarea 3 del plan: entidades `Usuario`, `Recurso` (`SalaReunion`, `Vehiculo`, `Equipo`) y `Reserva` con 10 `CHECK` con nombre y 2 índices; `entidades.py`; `seed.py` (`cargar_datos` + `main`); en `database.py`, `tipo_enum` (los enums se leen como enum, guardados como `VARCHAR`) y `es_local` (protege `recrear_esquema`). `modelo_bd.puml`: `creada_en` → `TIMESTAMPTZ`. Verificada contra el PostgreSQL de Compose: DDL, seed real, `\dT` vacío y cada INSERT inválido frenado por su `CHECK`.
- Tarea 6 del plan: `README.md` (el seed en el bloque del backend, con su nota) y la regla 2 (`hora_fin` como muy tarde las 23:59).
- Revisión final `dev:revisar-cambios` a nivel completo (desde `ec5a664`): sin bloqueos. Aplicado: `CHECK ck_reserva_hora_fin_maxima` (probado: `24:00` y `23:59:30` fallan), la tabla de decisiones del plan (0003 original + fila 0007), la línea del frontend en el plan y gotchas en el contexto del verificador y del revisor de código. Descartado por el usuario: ampliar `es_local` a `?host=` en la URL (innecesario para la prueba).
- Tarea 5 del plan: módulo `recursos` con el mismo patrón. `GET /recursos` devuelve los 8 recursos ordenados por nombre como unión discriminada por `tipo` (`SalaReunionRespuesta` con capacidad y aforo; `VehiculoRespuesta`, `EquipoRespuesta`); modalidad e imagen salen de las constantes de clase. Verificada contra Compose: orden, campos por tipo, `oneOf` con discriminador y `tipo` obligatorio en OpenAPI.
- Tarea 4 del plan: módulo `usuarios` (repository, dto, service, controller), con un proveedor `Depends` por capa junto a su clase. `GET /usuarios` devuelve los 4 usuarios ordenados por apellidos. `main.py` registra las entidades con `from app import entidades`, conserva el CORS y ya no tiene `GET /`; el frontend deja de pedirlo. Verificada contra el PostgreSQL de Compose (200, orden, CORS y enum `rol` en OpenAPI).
- PostgreSQL en Docker Compose (decisión 0007): en la máquina local no había PostgreSQL instalado. `docker-compose.yml` con el puerto solo en `127.0.0.1`; desde el devcontainer llega por `host.docker.internal:5432` (comprobado con `pg_isready` y `psql`). `.env.example` con las credenciales del compose; el usuario ya copió el `.env`.
- Comprobación de conexión: `app.ts` hace `fetch` a `GET /`, `/usuarios` y `/recursos` de `localhost:8000` y pinta código y cuerpo, sin estilos (el usuario lo quiere mínimo). `main.py` permite CORS para `localhost:4200`. Pide `/usuarios` y `/recursos`, los dos con 200.

## Pendiente
- Plan de reservas: validar en la API que las horas van en minutos, sin segundos (regla 2); decidir cómo se muestra el último minuto del día en la disponibilidad (regla 20).
- Diferido de la revisión final del backend: `length=None` sobra en `tipo_enum`; `dict` sin tipar en `recursos/service.py`. (La página provisional del frontend ya se retiró.)
- Diferido de la revisión del listado: el estilo global de `button` pasará a una clase `.boton` con variantes cuando haya más botones (aprobar, rechazar); un único sitio para el color por tipo; un título de pestaña por ruta.
- Los revisores (subagentes) siguen viendo un `CLAUDE.md` con `docs/notas` y `docs/plans`, aunque el fichero ya dice `.claude/`: descartar ese hallazgo si vuelve a salir.

## Siguiente paso
El plan de reservas (crear, aprobar, rechazar, cancelar, transferir y consultar disponibilidad, con los errores del dominio y la cabecera `X-Usuario-Id`), escrito con el formato de `dev:arquitecto` y revisado con `dev:revisar-plan`.

## Sin commit
- Nada.

## Preguntas abiertas
- Ninguna.

## Decisiones de este trabajo
- Decisiones [0001](../../docs/decisiones/0001-monolito-modular-por-capas.md) a [0010](../../docs/decisiones/0010-estilos-scss-y-variables-css.md); la [0003](../../docs/decisiones/0003-postgresql-local-create-all.md) está sustituida por la 0007.
