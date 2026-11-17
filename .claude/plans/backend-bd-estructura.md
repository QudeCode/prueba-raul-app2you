# Plan · Base de datos y estructura del backend

## Contexto
El modelado está cerrado:
- diagrama de clases (`docs/diagramas/modelo_recursos.puml`);
- diagrama de BD (`docs/diagramas/modelo_bd.puml`);
- reglas de negocio (`docs/reglas_negocio.md`);
- decisiones de negocio (`docs/apuntes.md`).

El backend solo tiene un "Hello world". Este plan monta PostgreSQL y la estructura por capas (controller → service → repository) siguiendo el flujo de ai-bank. Termina con dos lecturas reales que demuestran que las capas encajan: `GET /usuarios` y `GET /recursos`. La lógica de reservas y los errores del dominio van en el plan siguiente.

Lo que ha decidido el usuario:
- un fichero por capa en cada módulo;
- PostgreSQL con la configuración más sencilla posible;
- código en español;
- alcance "estructura + 2 lecturas";
- sin tests en el repositorio (el enunciado no los pide);
- PostgreSQL en Docker Compose (decisión 0007, que sustituye a la 0003: al empezar la tarea 3 resultó que no había PostgreSQL instalado en la máquina);
- las reservas por horas acaban como muy tarde a las 23:59.

## Mapa del código
- `src/backend/app/main.py`: solo `GET /` con "Hello world". Se sustituye.
- `src/backend/requirements.txt`: `fastapi` y `uvicorn[standard]`, sin versión fijada.
- `docs/diagramas/modelo_bd.puml` y `modelo_recursos.puml`: son la fuente de las columnas, la nulabilidad y los enums.
- `docs/reglas_negocio.md`: las reglas 1 a 20.
- No hay `CLAUDE.md` ni `.claude/context/`. Las decisiones 0001 a 0006 ya están en `docs/decisiones/`, aceptadas.

## Flujo de trabajo (ai-bank)
0. **Contexto del proyecto:** ejecutas `/core:init-context`, un comando que solo puede lanzar el usuario. Si no estuviera disponible, escribo yo `CLAUDE.md` y `.claude/context/` a partir de la plantilla del banco. En los dos casos deben recoger:
   - **autoría:** commits a nombre de Raúl Quirós, sin `Co-Authored-By`;
   - **idioma:** español;
   - **rama:** `master`;
   - **comandos:** los de la sección Verificación.
1. **Decisiones:** escribo las decisiones 0001 a 0006 y su índice en `docs/decisiones/`, en estado `propuesta`. Tú las aceptas.
2. **Plan:** este fichero. Ya pasó la revisión de 4 roles a nivel `completo`, y sus hallazgos están incorporados.
3. **Implementar** en la sesión principal, en el orden de las Tareas.
4. **Revisar:** workflow `dev:revisar-cambios`, nivel `completo`.
5. **Commit** con la fecha y el mensaje que me indiques.

## Decisiones a registrar (`docs/decisiones/`)
| Nº | Decisión |
|---|---|
| 0001 (ADR) | Monolito dividido en módulos (`usuarios`, `recursos`, `reservas`) con capas controller/service/repository y un fichero por capa: `controller.py`, `dto.py`, `service.py`, `repository.py`, `entity.py`. Reglas: el controller no importa entidades; el repository no importa DTO; el servicio hace las conversiones (sin Mapper) y devuelve DTO |
| 0002 | FastAPI + SQLAlchemy 2.0 síncrono + Pydantic v2. Sin SQLModel, porque mezcla DTO y entidad. Conexión entre capas con `Depends`. La sesión por petición no hace commit automático: los servicios que escriben hacen commit de forma explícita, antes de responder |
| 0003 (ADR), sustituida por 0007 | PostgreSQL en Docker Compose (`docker compose up -d`), configurado con `DATABASE_URL` en `.env`. Esquema con `create_all` desde un script que también carga datos de prueba. Sin migraciones; Alembic sería el camino si el proyecto creciera |
| 0004 | Enums como `StrEnum`, guardados como `VARCHAR` + `CHECK` generado desde el propio enum. Las invariantes de una sola fila también llevan `CHECK` con nombre. Las horas son `TIME` y una reserva por horas acaba como muy tarde a las 23:59 (Python no puede representar las 24:00) |
| 0005 | Herencia de recursos en una sola tabla `recurso` con la columna discriminadora `tipo`. `MODALIDAD_RESERVA` e `IMAGEN` son constantes de clase, no columnas. Las imágenes son ficheros fijos del frontend; la API devuelve su nombre |
| 0006 | Código en español para el dominio y en inglés para los nombres de las capas |

Se dejan para el plan de reservas, que es donde se usan: los errores del dominio con su manejador (404/403/400/409) y el usuario actual por la cabecera `X-Usuario-Id`.

## Cambios por fichero

**Infraestructura**
- `src/backend/.env.example`: `DATABASE_URL=postgresql+psycopg://reservas:reservas@localhost:5432/reservas` (las credenciales de `docker-compose.yml`), con un comentario: desde el devcontainer, el host es `host.docker.internal`.
- `docker-compose.yml` (decisión 0007): PostgreSQL 17, puerto publicado en `127.0.0.1:5432` y volumen con nombre.
- `.gitignore`: añadir `.env`.
- `src/backend/requirements.txt` con versiones mínimas:
  - `fastapi>=0.115`, `uvicorn[standard]`
  - `sqlalchemy>=2.0`, `psycopg[binary]>=3.2`, `pydantic>=2.7`, `pydantic-settings>=2.4`

**Base común (`src/backend/app/`)**
- `config.py`: `Settings(BaseSettings)` con `database_url`, leído del fichero `.env`.
- `database.py`:
  - `engine`, `SessionLocal` y `Base(DeclarativeBase)`;
  - `get_session()`: abre la sesión y la cierra al acabar. Si quedó algo sin confirmar, se deshace; nunca hace commit;
  - `tipo_enum(enum)`: tipo de columna `VARCHAR` que se lee como el enum (sin tipo nativo ni `CHECK` automático);
  - `check_enum(columna, enum, nombre)`: crea el `CheckConstraint` a partir de los valores del `StrEnum`;
  - `es_local(url)`: si el host es local (`None`, `localhost`, `127.0.0.1`, `::1`, `host.docker.internal`);
  - `recrear_esquema(engine)`: se niega (`RuntimeError`) si la base no es local; importa `app.entidades` y ejecuta `drop_all` + `create_all`.
- `entidades.py` (tarea 3, cuando existen las entidades): importa las tres entidades para que todas queden registradas. Lo usan `main.py`, `seed.py` y `recrear_esquema`.
- Columnas de enum: `mapped_column(tipo_enum(<Enum>))` más su `check_enum`. Sin `tipo_enum`, SQLAlchemy crearía un ENUM nativo de PostgreSQL, que la decisión 0004 descarta.
- `common/enums.py`, con los valores copiados de `modelo_recursos.puml` (el valor de cada miembro es igual a su nombre):
  - `Rol`: TRABAJADOR, RESPONSABLE
  - `TipoRecurso`: SALA_REUNION, VEHICULO, EQUIPO
  - `PoliticaCancelacion`: FLEXIBLE, MODERADA, BLOQUEADA
  - `ModalidadReserva`: POR_HORAS, DIA_COMPLETO, AMBAS
  - `EstadoReserva`: PENDIENTE, APROBADA, RECHAZADA, CANCELADA
- `main.py`: crea la app, importa `app.entidades` e incluye los routers de usuarios y recursos.

**Módulo `usuarios/`**
- `entity.py`: `Usuario`, tabla `usuario`. `id` es la clave primaria; `nombre`, `apellidos` y `rol` son obligatorios; `CHECK ck_usuario_rol`.
- `repository.py`: `UsuarioRepository(session).listar()`, ordenado por apellidos, nombre e id.
- `service.py`: `UsuarioService(repo).listar() -> list[UsuarioRespuesta]`.
- `dto.py`: `UsuarioRespuesta` con `id`, `nombre`, `apellidos` y `rol`, y `from_attributes=True`.
- `controller.py`: `GET /usuarios`, que devuelve `list[UsuarioRespuesta]`.

**Módulo `recursos/`**
- `entity.py`, tabla `recurso`:
  - **Columnas:** `id` (clave primaria). Obligatorias: `tipo`, `nombre`, `descripcion` y `politica_cancelacion`. Pueden ir vacías: `capacidad_maxima` y `aforo_compartido`, declaradas en la base porque es una sola tabla.
  - **Herencia:** `Recurso` usa `polymorphic_on=tipo`. `SalaReunion`, `Vehiculo` y `Equipo` tienen como identidad `TipoRecurso.SALA_REUNION`, `VEHICULO` y `EQUIPO`.
  - **Constantes:**

    | Clase | `MODALIDAD_RESERVA` | `IMAGEN` |
    |---|---|---|
    | `SalaReunion` | `POR_HORAS` | `"sala.png"` |
    | `Vehiculo` | `DIA_COMPLETO` | `"vehiculo.png"` |
    | `Equipo` | `AMBAS` | `"equipo.png"` |

  - **`CHECK`:**
    - `ck_recurso_tipo` y `ck_recurso_politica`, generados desde sus enums;
    - `ck_recurso_campos_tipo`: cada tipo con sus campos rellenos y los ajenos vacíos (sala: `capacidad_maxima` y `aforo_compartido`; vehículo: `matricula` y `plazas`; equipo: `numero_serie`);
    - `ck_recurso_capacidad`: `capacidad_maxima IS NULL OR capacidad_maxima > 0`;
    - `ck_recurso_plazas`: `plazas IS NULL OR plazas > 0`;
    - `uq_recurso_matricula` y `uq_recurso_numero_serie`: únicos.
- `repository.py`: `listar()`, ordenado por nombre e id.
- `dto.py`:
  - **Campos comunes:** `id`, `nombre`, `descripcion`, `politica_cancelacion`, `imagen` y `modalidad_reserva`.
  - **Una respuesta por tipo:** `SalaReunionRespuesta` (añade `capacidad_maxima` y `aforo_compartido`), `VehiculoRespuesta` (`matricula` y `plazas`) y `EquipoRespuesta` (`numero_serie`). Cada una lleva `tipo: Literal[...]`.
  - **`RecursoRespuesta`:** `Annotated[SalaReunionRespuesta | VehiculoRespuesta | EquipoRespuesta, Field(discriminator="tipo")]`.
- `service.py`: `_a_respuesta(recurso)` elige el DTO según el tipo y lo construye de forma explícita, con `imagen` y `modalidad_reserva` sacados de las constantes de la clase.
- `controller.py`: `GET /recursos`, que devuelve `list[RecursoRespuesta]`.

**Módulo `reservas/`** (en este plan solo la tabla)
- `entity.py`, tabla `reserva`:
  - **Columnas obligatorias:**
    - `id` (clave primaria);
    - `recurso_id`, `titular_id`;
    - `fecha DATE`, `estado`;
    - `creada_en TIMESTAMPTZ`, con `now()` como valor por defecto.
  - **Pueden ir vacías:** `aprobada_por_id`, `hora_inicio TIME`, `hora_fin TIME` y `asistentes_sala`.
  - **Relaciones:** `recurso`, `titular` y `aprobada_por`, sin relación inversa.
  - **`CHECK`:**
    - `ck_reserva_estado`, generado desde el enum;
    - `ck_reserva_horas_juntas`: `(hora_inicio IS NULL) = (hora_fin IS NULL)`;
    - `ck_reserva_horas_orden`: `hora_inicio < hora_fin`;
    - `ck_reserva_asistentes`: `asistentes_sala IS NULL OR asistentes_sala >= 1`;
    - `ck_reserva_aprobada_con_aprobador`: `estado <> 'APROBADA' OR aprobada_por_id IS NOT NULL`.
  - **Índices:** `ix_reserva_recurso_fecha` en `(recurso_id, fecha)` e `ix_reserva_titular`.
- Las reglas que mezclan tablas (la modalidad según el tipo, `asistentes_sala` solo en salas con aforo compartido) van en el servicio, en el plan siguiente.

**Datos de prueba**
- `app/seed.py` (`python -m app.seed`):
  - imprime a qué base se conecta y llama a `recrear_esquema(engine)`, que solo actúa sobre una base local (si no, el seed termina con el mensaje);
  - `cargar_datos(session)` añade los datos sin commit; `main()` hace el commit;
  - usuarios: Ana García (TRABAJADOR), Luis Pérez (TRABAJADOR), Marta López (RESPONSABLE) y Jordi Puig (RESPONSABLE);
  - recursos:
    - **salas:** "Sala Mar" (capacidad 10, aforo compartido, FLEXIBLE), "Sala Montaña" (capacidad 6, sin aforo compartido, MODERADA) y "Auditorio" (capacidad 50, aforo compartido, BLOQUEADA);
    - **vehículos:** "Furgoneta 1" (4821 LKM, 3 plazas, MODERADA) y "Coche eléctrico" (7306 MRT, 5 plazas, FLEXIBLE);
    - **equipos:** "Proyector portátil" (PRY-2041, FLEXIBLE), "Portátil de préstamo" (PRT-1187, MODERADA) y "Cámara de vídeo" (CAM-0532, BLOQUEADA).
- Las reservas aleatorias se generarán en el plan siguiente, a través del servicio, para que cumplan las reglas.

**Documentación**
- `README.md`: cargar los datos de prueba (`python -m app.seed`). El requisito de Docker, `docker compose up -d` y la copia del `.env` ya están (decisión 0007).
- `docs/diagramas/modelo_bd.puml`: `creada_en` pasa a `TIMESTAMPTZ` (hecho en la tarea 3).
- `docs/reglas_negocio.md`, regla 2: "una reserva por horas acaba como muy tarde a las 23:59".

## Tareas (en orden)
1. Infraestructura: `.env.example`, `.gitignore` y `requirements.txt`.
2. Base común: config, database y enums.
3. Las tres entidades, `entidades.py` y el script de datos de prueba. Comprobar en `psql` las tablas y los `CHECK`, y que `\dT` no lista tipos enum.
4. Módulo usuarios y `GET /usuarios`.
5. Módulo recursos y `GET /recursos`.
6. README y la regla 2.

## Riesgos
- **PostgreSQL en Docker Compose:** se arranca en local (no dentro del devcontainer) y desde el devcontainer se llega por `host.docker.internal:5432`.
- **Versiones de Python distintas:** el sistema tiene la 3.11, el `.venv` es 3.13 y está fijada la 3.12. El código será compatible con 3.11 o superior.

## Verificación
No hay tests en el repositorio. Las comprobaciones se hacen a mano o con scripts temporales fuera del repo:
- `docker compose up -d` (en la raíz), `cd src/backend && cp .env.example .env` y `pip install -r requirements.txt`.
- `python -m app.seed`, y después `psql … -c '\d+ reserva'` para ver las columnas, los `CHECK` y los índices.
- Intentar con `psql` los INSERT que deben fallar: una sala sin capacidad, horas invertidas, una reserva aprobada sin aprobador, un estado desconocido.
- `uvicorn app.main:app --reload`, y después `GET /usuarios` y `GET /recursos` desde `/docs`. Swagger debe mostrar la respuesta según el `tipo`.
- Workflow `dev:revisar-cambios` a nivel `completo`, sin problemas que bloqueen.
