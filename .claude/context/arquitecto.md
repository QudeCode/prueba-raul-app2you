# Contexto · arquitecto

## Dónde van los planes
`.claude/plans/<slug>.md`, slug en kebab-case y en español.

## Arquitectura vigente
- Decisiones 0001 a 0006 en `docs/decisiones/` (capas, stack, PostgreSQL, enums y CHECK, herencia de recursos, idioma).
- Modelo: `docs/diagramas/modelo_recursos.puml` (clases) y `docs/diagramas/modelo_bd.puml` (tablas).
- Reglas de negocio numeradas: `docs/reglas_negocio.md`. Un plan las cita por número.

## Reutilizar antes de crear
- `src/backend/app/database.py`: `get_session`, `check_enum`, `recrear_esquema`.
- `src/backend/app/common/enums.py`: todos los enums del dominio.
- `src/backend/app/entidades.py`: registro único de entidades.

## Gotchas
- Sin tareas de tests (regla dura de `CLAUDE.md`).
- Las reglas que cruzan tablas (modalidad según tipo, `asistentes_sala` solo en salas con aforo compartido) van en el servicio, no en CHECK.
- Una reserva por horas acaba como muy tarde a las 23:59 (decisión 0004).
- Los servicios que escriben hacen commit explícito; `get_session` nunca hace commit (decisión 0002).
