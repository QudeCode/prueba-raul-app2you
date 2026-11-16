# 0003 · PostgreSQL local y esquema con create_all

Estado: aceptada
Tipo: ADR

## Contexto
El enunciado exige persistencia en base de datos y recomienda no perder tiempo en configuraciones complejas. No hay despliegues: solo se ejecuta en local.

## Decisión
Se usa PostgreSQL instalado en la máquina de quien ejecuta el proyecto, sin Docker. La conexión se configura con `DATABASE_URL` en `src/backend/.env`. El esquema se crea con `create_all` desde un script (`python -m app.seed`) que borra y vuelve a crear las tablas y carga datos de prueba.

## Alternativas descartadas
- SQLite: sin experiencia previa y sin las garantías de PostgreSQL.
- PostgreSQL en Docker o dentro del devcontainer: más piezas y conflictos de puertos con el PostgreSQL ya instalado.
- Migraciones con Alembic: sin despliegues no aportan nada; añaden configuración y comandos.

## Consecuencias
- Hay que crear la base `reservas` antes de ejecutar el seed.
- Desde el devcontainer, el host de la base es `host.docker.internal`.
- Cualquier cambio de esquema exige volver a ejecutar el seed, que borra los datos.
- Si el proyecto creciera o se desplegara, el camino es Alembic con una migración inicial generada desde las entidades.
