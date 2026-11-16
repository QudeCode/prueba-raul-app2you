# Contexto · verificador

## Dónde se ejecuta
En el devcontainer, con un venv propio fuera del repo (nunca `src/backend/.venv`). PostgreSQL en `host.docker.internal:5432`. Si algo falla solo por el entorno del contenedor, dilo: la referencia es la máquina local.

## Rama base
`master`.

## Comprobaciones por app
- Backend: que importe (`python -c "import app.main"` desde `src/backend`), que arranque con uvicorn y, si hay base disponible, que `python -m app.seed` funcione.
- Frontend: `npm run build` en `src/frontend`.

## Gotchas
- No hay tests a propósito: su ausencia no es un fallo.
