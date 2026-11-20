# Contexto · verificador

## Dónde se ejecuta
En el devcontainer, con un venv propio fuera del repo (nunca `src/backend/.venv`). El PostgreSQL de Docker Compose en `host.docker.internal:5432`. Si algo falla solo por el entorno del contenedor, dilo: la referencia es la máquina local.

## Rama base
`master`.

## Comprobaciones por app
- Backend: que importe (`python -c "import app.main"` desde `src/backend`), que arranque con uvicorn y, si hay base disponible, que `python -m app.seed` funcione.
- Frontend: `npm run build` en `src/frontend`.

## Gotchas
- No hay tests a propósito: su ausencia no es un fallo.
- `DATABASE_URL` no se lee de `.env` (está denegado): expórtala en el entorno, que manda sobre `.env`. La del Compose desde el contenedor es `postgresql+psycopg://reservas:reservas@host.docker.internal:5432/reservas` (credenciales de desarrollo, las mismas de `.env.example`). Con `localhost` no llega.
- `src/frontend/node_modules` es el de la máquina local (esbuild compilado para su sistema): `npm run build` falla en el devcontainer. Compila una copia del frontend sin `node_modules` con su propio `npm ci`, fuera del repo.
- `python -m app.seed` borra y recrea las tablas: solo con autorización explícita en el encargo.
- No hay linter ni mypy: como comprobación mínima del backend, `PYTHONDONTWRITEBYTECODE=1 python -m compileall -q app`.
- Copia del frontend: `tar --exclude=node_modules --exclude=dist --exclude=.angular` y `npm ci`; compila en segundos.
