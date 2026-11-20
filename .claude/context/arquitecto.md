# Contexto · arquitecto

## Dónde van los planes
`.claude/plans/<slug>.md`, slug en kebab-case y en español.

## Arquitectura vigente
- Decisiones 0001 a 0016 en `docs/decisiones/`; la 0003 está sustituida por la 0007, y la ruta de la disponibilidad de la 0012, por la 0015.
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
- Si no hay código que explorar (módulo o proyecto nuevo), el plan puede escribirlo la sesión principal con el formato de dev:arquitecto; la revisión con dev:revisar-plan no se salta.
- Las reglas de `docs/reglas_negocio.md` no se renumeran: una regla nueva toma el siguiente número libre y, si va en medio de una sección, se escribe `N)` para que Markdown no la renumere.
- En FastAPI, las rutas fijas (`/reservas/mias`) se declaran antes que las de parámetro (`/reservas/{id}`).
- Si una transacción modifica filas que no ha bloqueado con `FOR UPDATE`, puede pisar el cambio de otra que sí las bloqueó: hay que leerlas con `with_for_update(of=…)` y `populate_existing`.
