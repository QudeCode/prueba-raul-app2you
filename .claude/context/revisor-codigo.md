# Contexto · revisor-codigo

## Alcance por defecto
Rama base `master`. Fuera de la revisión: `package-lock.json`, `.venv/`, `dist/`, `.angular/`.

## Modelo de seguridad
Sin autenticación (prueba técnica). El usuario actual llega por la cabecera `X-Usuario-Id`; su rol se lee siempre de la base de datos, nunca del cliente.

## Convenciones que se revisan
- Capas de la decisión 0001: el controller no importa entidades; el repository no importa DTO; el servicio devuelve DTO.
- Enums como `StrEnum` con `CHECK` generado por `check_enum` (decisión 0004).
- Dominio en español, nombres de capa en inglés (decisión 0006).
- Reglas de negocio citadas por su número de `docs/reglas_negocio.md`.

## Gotchas
- No pedir tests: el proyecto no los lleva, a propósito.
