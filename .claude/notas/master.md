# master · Base de datos y estructura del backend

Rama: master · Plan: [backend-bd-estructura](../plans/backend-bd-estructura.md)

## Objetivo
Montar PostgreSQL y la estructura por capas del backend (controller → service → repository) con dos lecturas que demuestran que encajan: `GET /usuarios` y `GET /recursos`. La lógica de reservas va en un plan posterior.

## Hecho
- Modelado cerrado: diagramas de clases y BD, `docs/reglas_negocio.md` (reglas 1 a 20) y decisiones de negocio en `docs/apuntes.md`.
- Decisiones técnicas 0001 a 0006 aceptadas (`docs/decisiones/`).
- Plan aprobado y revisado por `dev:revisar-plan` a nivel completo, con sus hallazgos incorporados.
- Contexto de ai-bank: `CLAUDE.md`, `.claude/context/` (6 agentes de `dev`) y `.claude/settings.json`.
- Tarea 1 del plan: `requirements.txt` con versiones mínimas, `.env.example` y `.env` en `.gitignore`.
- Tarea 2 del plan (revisada con `dev:revisar-plan`): `app/config.py`, `app/database.py` (`get_session`, `check_enum`, `recrear_esquema`) y `app/common/enums.py`. Verificada con un script temporal fuera del repo; `recrear_esquema` y la conexión real se prueban en la tarea 3.
- Comprobación de conexión: `app.ts` hace `fetch` a `GET /`, `/usuarios` y `/recursos` de `localhost:8000` y pinta código y cuerpo, sin estilos (el usuario lo quiere mínimo). `main.py` permite CORS para `localhost:4200`. Probado en local: `/` da 200; `/usuarios` y `/recursos`, 404 hasta las tareas 4 y 5. Al reescribir `main.py` en la tarea 4 hay que conservar el CORS.

## Pendiente
- Tareas 3 a 6 del plan.
- Al acabar: workflow `dev:revisar-cambios` a nivel `completo` y commit (con la aprobación del usuario).
- Documentos que el plan actualiza en la tarea 6: `README.md` (PostgreSQL local, `.env`, seed), `docs/diagramas/modelo_bd.puml` (`creada_en` → `TIMESTAMPTZ`) y la regla 2 de `docs/reglas_negocio.md` (hora fin máxima 23:59).

## Siguiente paso
Tarea 3 del plan: las entidades de `usuarios`, `recursos` y `reservas` (columnas de enum con `String` explícito y `check_enum`), `app/entidades.py` y `app/seed.py`. Necesita PostgreSQL accesible para probar el seed.

## Sin commit
- Nada.

## Preguntas abiertas
- Para probar desde el contenedor, el PostgreSQL de la máquina local tiene que estar arrancado y aceptar conexiones desde `host.docker.internal`. Si no, las pruebas de base de datos se hacen en local.

## Decisiones de este trabajo
- Decisiones [0001](../../docs/decisiones/0001-monolito-modular-por-capas.md) a [0006](../../docs/decisiones/0006-idioma-del-codigo.md).
