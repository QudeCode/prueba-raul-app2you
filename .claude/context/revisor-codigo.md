# Contexto · revisor-codigo

## Alcance por defecto
Rama base `master`. Fuera de la revisión: `package-lock.json`, `.venv/`, `dist/`, `.angular/`.

## Modelo de seguridad
Sin autenticación (prueba técnica). El usuario actual llega por la cabecera `X-Usuario-Id`; su rol se lee siempre de la base de datos, nunca del cliente.

## Convenciones que se revisan
- Capas de la decisión 0001: el controller no importa entidades; el repository no importa DTO; el servicio devuelve DTO.
- Enums como `StrEnum` con `CHECK` generado por `check_enum` (decisión 0004).
- Capas del frontend (decisión 0008): un componente presentacional no inyecta servicios; una página no usa `HttpClient` (pasa por el servicio de su funcionalidad); la lógica de negocio va en funciones puras del dominio, no en componentes; `reservas` puede usar el modelo de `recursos`, nunca al revés; lo compartido va en `app/common/`.
- Cada regla de una sola fila de `docs/reglas_negocio.md` (también los límites de hora, como las 23:59) tiene su `CheckConstraint` con nombre en la entidad (decisión 0004).
- Dominio en español, nombres de capa en inglés (decisión 0006).
- Reglas de negocio citadas por su número de `docs/reglas_negocio.md`.

## Gotchas
- Los ficheros nuevos sin seguimiento no salen en `git diff`: si el `--stat` no incluye carpetas nuevas del plan, léelas directamente.
- `src/frontend/public/` se copia entero al build: nada que no deba publicarse (zip, material con licencia restrictiva) puede quedarse ahí.
- No pedir tests: el proyecto no los lleva, a propósito.
