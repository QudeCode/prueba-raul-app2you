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

## Pendiente
- Tareas 2 a 6 del plan.
- Al acabar: workflow `dev:revisar-cambios` a nivel `completo` y commit (con la aprobación del usuario).
- Documentos que el plan actualiza en la tarea 6: `README.md` (PostgreSQL local, `.env`, seed), `docs/diagramas/modelo_bd.puml` (`creada_en` → `TIMESTAMPTZ`) y la regla 2 de `docs/reglas_negocio.md` (hora fin máxima 23:59).

## Siguiente paso
Tarea 2 del plan: `app/config.py`, `app/database.py` (`get_session`, `check_enum`, `recrear_esquema`), `app/entidades.py` y `app/common/enums.py`.

## Sin commit
- `.claude/notas/master.md` (este traspaso).

## Preguntas abiertas
- Para probar desde el contenedor, el PostgreSQL de la máquina local tiene que estar arrancado y aceptar conexiones desde `host.docker.internal`. Si no, las pruebas de base de datos se hacen en local.

## Decisiones de este trabajo
- Decisiones [0001](../../docs/decisiones/0001-monolito-modular-por-capas.md) a [0006](../../docs/decisiones/0006-idioma-del-codigo.md).
