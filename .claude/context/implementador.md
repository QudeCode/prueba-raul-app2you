# Contexto · implementador

## Apps y rutas
- Backend: `src/backend/app/<módulo>/{controller,dto,service,repository,entity}.py` (decisión 0001).
- Frontend: `src/frontend` (Angular 22).

## Skills de stack que cargar
Ninguna: no hay plugin de stack para FastAPI ni Angular.

## Reutilizar antes de crear
- `app/database.py` (`get_session`, `check_enum`, `recrear_esquema`), `app/common/enums.py`, `app/entidades.py`.

## No tocar
- `src/backend/.venv` (es el de la máquina local) y cualquier `.env`.

## Cómo verificar lo que implementas
Con un venv propio fuera del repo (`pip install -r src/backend/requirements.txt`) y el PostgreSQL de Docker Compose en `host.docker.internal:5432`. El resultado en la máquina local es el que vale.

## Gotchas
- No añadir tests ni dependencias de test.
