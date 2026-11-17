# master · Base de datos y estructura del backend

Rama: master · Plan: [backend-bd-estructura](../plans/backend-bd-estructura.md)

## Objetivo
Montar PostgreSQL y la estructura por capas del backend (controller → service → repository) con dos lecturas que demuestran que encajan: `GET /usuarios` y `GET /recursos`. La lógica de reservas va en un plan posterior.

## Hecho
- Modelado cerrado: diagramas de clases y BD, `docs/reglas_negocio.md` (reglas 1 a 20) y decisiones de negocio en `docs/apuntes.md`.
- Decisiones técnicas 0001 a 0007 aceptadas (`docs/decisiones/`); la 0003 está sustituida por la 0007.
- Plan aprobado y revisado por `dev:revisar-plan` a nivel completo, con sus hallazgos incorporados.
- Contexto de ai-bank: `CLAUDE.md`, `.claude/context/` (6 agentes de `dev`) y `.claude/settings.json`.
- Tarea 1 del plan: `requirements.txt` con versiones mínimas, `.env.example` y `.env` en `.gitignore`.
- Tarea 2 del plan (revisada con `dev:revisar-plan`): `app/config.py`, `app/database.py` (`get_session`, `check_enum`, `recrear_esquema`) y `app/common/enums.py`. Verificada con un script temporal fuera del repo; `recrear_esquema` y la conexión real se prueban en la tarea 3.
- Tarea 3 del plan: entidades `Usuario`, `Recurso` (`SalaReunion`, `Vehiculo`, `Equipo`) y `Reserva` con 10 `CHECK` con nombre y 2 índices; `entidades.py`; `seed.py` (`cargar_datos` + `main`); en `database.py`, `tipo_enum` (los enums se leen como enum, guardados como `VARCHAR`) y `es_local` (protege `recrear_esquema`). `modelo_bd.puml`: `creada_en` → `TIMESTAMPTZ`. Verificada contra el PostgreSQL de Compose: DDL, seed real, `\dT` vacío y cada INSERT inválido frenado por su `CHECK`.
- PostgreSQL en Docker Compose (decisión 0007): en la máquina local no había PostgreSQL instalado. `docker-compose.yml` con el puerto solo en `127.0.0.1`; desde el devcontainer llega por `host.docker.internal:5432` (comprobado con `pg_isready` y `psql`). `.env.example` con las credenciales del compose; el usuario ya copió el `.env`.
- Comprobación de conexión: `app.ts` hace `fetch` a `GET /`, `/usuarios` y `/recursos` de `localhost:8000` y pinta código y cuerpo, sin estilos (el usuario lo quiere mínimo). `main.py` permite CORS para `localhost:4200`. Probado en local: `/` da 200; `/usuarios` y `/recursos`, 404 hasta las tareas 4 y 5. Al reescribir `main.py` en la tarea 4 hay que conservar el CORS.

## Pendiente
- Tareas 4 a 6 del plan.
- Al acabar: workflow `dev:revisar-cambios` a nivel `completo` y commit (con la aprobación del usuario).
- Documentos que el plan actualiza en la tarea 6: `README.md` (cargar los datos de prueba; Docker Compose y `.env` ya están) y la regla 2 de `docs/reglas_negocio.md` (hora fin máxima 23:59).

## Siguiente paso
Tarea 4 del plan: módulo `usuarios` (controller, service, repository, dto) y `GET /usuarios`. `main.py` importa `app.entidades` e incluye el router, conservando el CORS.

## Sin commit
- PostgreSQL en Docker Compose: `docker-compose.yml`, `.env.example`, decisión 0007 y la documentación que la cita.
- Tarea 3: entidades, `entidades.py`, `seed.py`, cambios en `database.py`, `modelo_bd.puml` y el plan del backend.

## Preguntas abiertas
- Ninguna.

## Decisiones de este trabajo
- Decisiones [0001](../../docs/decisiones/0001-monolito-modular-por-capas.md) a [0007](../../docs/decisiones/0007-postgresql-docker-compose.md); la [0003](../../docs/decisiones/0003-postgresql-local-create-all.md) está sustituida por la 0007.
