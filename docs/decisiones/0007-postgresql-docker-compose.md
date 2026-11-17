# 0007 · PostgreSQL en Docker Compose

Estado: aceptada
Tipo: ADR
Sustituye a: [0003](0003-postgresql-local-create-all.md)

## Contexto
La decisión 0003 suponía un PostgreSQL ya instalado en la máquina de desarrollo, y no lo había. Hace falta una base que arranque igual en cualquier máquina, también en la de quien revise el proyecto, sin instalar ni configurar PostgreSQL.

## Decisión
PostgreSQL 17 corre en Docker Compose (`docker-compose.yml` en la raíz; `docker compose up -d`), con el puerto 5432 publicado solo en `127.0.0.1` y credenciales de desarrollo fijas (`reservas`/`reservas`). La conexión se configura con `DATABASE_URL` en `src/backend/.env`, copiado de `.env.example` sin cambios. El esquema se crea con `create_all` desde `python -m app.seed`, que borra y vuelve a crear las tablas y carga datos de prueba. Sin migraciones.

## Alternativas descartadas
- PostgreSQL instalado en la máquina: obliga a instalarlo y configurarlo en cada una.
- PostgreSQL dentro del devcontainer: `.devcontainer/` no está en git y quien revise no lo usa.
- SQLite: sin las garantías de PostgreSQL.
- Migraciones con Alembic: sin despliegues no aportan nada.

## Consecuencias
- Requisito: Docker con `docker compose`.
- `docker compose up -d` se lanza en la máquina anfitriona, no dentro del devcontainer (tiene docker-in-docker y levantaría la base en un Docker interno). Desde el devcontainer, el host de la base es `host.docker.internal`.
- Las credenciales son solo de desarrollo; por eso el puerto no se expone a la red local.
- Si el puerto 5432 ya está ocupado en la máquina, `docker compose up` falla.
- Las variables `POSTGRES_*` solo se aplican al crear el volumen; para cambiarlas o empezar de cero: `docker compose down -v`.
- Cualquier cambio de esquema exige volver a ejecutar el seed, que borra los datos.
- Si el proyecto creciera o se desplegara, el camino es Alembic con una migración inicial generada desde las entidades.
