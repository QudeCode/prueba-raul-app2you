# Reservas — prueba técnica

Sistema de reservas de recursos empresariales (salas, vehículos, equipos) para una prueba técnica. Backend FastAPI + PostgreSQL y frontend Angular.

## Comandos
Todo se ejecuta en la máquina local, que es la referencia: si algo funciona en el entorno de Claude y no en local, manda la máquina local.
- Backend: `cd src/backend && source .venv/bin/activate && uvicorn app.main:app --reload` → http://localhost:8000/docs
- Instalar backend: `pip install -r requirements.txt` (dentro de `src/backend`, con el `.venv` activo)
- Datos de prueba (borra y recrea las tablas): `python -m app.seed`
- Frontend: `cd src/frontend && npm start` → http://localhost:4200
- Build frontend (comprueba tipos): `cd src/frontend && npm run build`
- Tests: no hay (ver Reglas duras).

## Reglas duras
- Sin tests en el repositorio: el enunciado no los pide y el tiempo se dedica al análisis, el modelado y la implementación. Claude puede probar con scripts temporales fuera del repo.
- `src/backend/.venv` es el de la máquina local: Claude no lo usa ni lo modifica. Para probar, Claude usa un venv propio fuera del repo.
- PostgreSQL está instalado en la máquina local, no en el devcontainer ni en Docker. Desde el contenedor se llega por `host.docker.internal:5432`.
- Antes de proponer algo, respetar el modelo y las reglas: `docs/reglas_negocio.md` (reglas numeradas) y los diagramas de `docs/diagramas/`.
- Diagramas PlantUML: solo clases, atributos, relaciones y enums; sin métodos, notas ni comentarios.

## Reglas sin excepción (candidatas a hook)
- No leer `.env*` (en `permissions.deny`).

## Git
- Rama de trabajo: `master`.
- Commits: solo con aprobación explícita del usuario. Los subagentes nunca hacen commit.
- Formato del mensaje: una frase breve en español que describe lo que se añade.
- Autoría: los commits van a nombre del usuario (Raúl Quirós), sin `Co-Authored-By`. El uso de IA se explica en el README, no en cada commit ni en comentarios del código.

## Documentación
- `docs/` es para cualquier lector (dentro de git); lo que solo sirve a la IA va en `.claude/`. Sin fechas en los documentos: describen el estado vigente.
- Dominio (`docs/`): `enunciado.md` (enunciado original), `reglas_negocio.md` (reglas numeradas), `apuntes.md` (decisiones de negocio y notas del usuario) y `diagramas/` (clases y BD).
- Decisiones técnicas: `docs/decisiones/` (índice en `README.md`). Antes de proponer algo, comprueba las vigentes.
- Notas de trabajo: `.claude/notas/<rama>.md`. Al empezar, `/core:retomar`; al pausar, `/core:traspaso`.
- Planes: `.claude/plans/`.
- La documentación se actualiza en el mismo paso que el código que describe.

## Idioma
Español en todo: código de dominio, comentarios, documentación, commits y respuestas. Los nombres de capa van en inglés (decisión 0006).

## Agentes del banco
Los agentes de `ai-bank` leen su contexto en `.claude/context/<agente>.md`, y las reglas de este fichero mandan sobre su método. Flujo de trabajo: skill `core:orquestacion`. Memoria: skill `core:memoria`. Al cerrar una feature: `/core:retro`.
