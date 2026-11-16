# Contexto · revisor-plan

## Reglas contra las que se revisa
`CLAUDE.md`, `docs/decisiones/`, `docs/reglas_negocio.md` y los diagramas de `docs/diagramas/`.

## Riesgos típicos del proyecto
- Solapes y capacidad con aforo compartido: se comprueba el momento de máxima ocupación, no la suma de todo lo que se solapa (regla 6).
- Concurrencia al reservar: dos peticiones no pueden pasar a la vez la comprobación de conflicto.
- Plazos de cancelación y transferencia según política (reglas 13 a 19), contados hasta el inicio de la reserva.
- Coherencia entre los DTO del backend y lo que consume el frontend.

## Fuera de alcance por defecto
- Pedir tests (el proyecto no los lleva, a propósito).
- Autenticación real (el usuario actual llega por cabecera `X-Usuario-Id`).
- Migraciones, Docker o despliegue (decisión 0003).

## Gotchas
