# Reservas — prueba técnica

Sistema de reservas de recursos empresariales (ver [enunciado](docs/enunciado.md)).

Las reglas de negocio acordadas están en [docs/reglas_negocio.md](docs/reglas_negocio.md).

| Capa     | Tecnología       | Carpeta         |
|----------|------------------|-----------------|
| Frontend | Angular 22       | `src/frontend/` |
| Backend  | Python · FastAPI | `src/backend/`  |

## Requisitos

| Herramienta | Versión mínima                         | Versión fijada                | Gestor recomendado                          |
|-------------|----------------------------------------|-------------------------------|---------------------------------------------|
| Node.js     | `^22.22.3` · `^24.15.0` · `>=26`        | `.nvmrc` → `24`               | [nvm](https://github.com/nvm-sh/nvm)        |
| Python      | `3.11`                                 | `.python-version` → `3.12`    | [pyenv](https://github.com/pyenv/pyenv)     |
| Docker      | con `docker compose`                   | —                             | [Docker Desktop](https://www.docker.com/products/docker-desktop/) |

La versión mínima de Node la impone Angular 22. Los ficheros de versión permiten que los gestores seleccionen la versión correcta automáticamente:

```bash
nvm install                      # instala y activa la versión de .nvmrc
pyenv install --skip-existing    # instala la versión de .python-version
```

> pyenv activa la versión al entrar en el directorio. Con nvm, en cada terminal nueva hay que ejecutar `nvm use`, salvo que tengas configurado el cambio automático.

## Ejecución

### Base de datos → PostgreSQL 17 en `localhost:5432`

Desde la raíz del repositorio, en una terminal de tu máquina:

```bash
docker compose up -d
cp src/backend/.env.example src/backend/.env
```

Las credenciales (`reservas`/`reservas`) son solo de desarrollo y el puerto se publica únicamente en `127.0.0.1`.

> Para empezar de cero (o si cambias las variables `POSTGRES_*` de `docker-compose.yml`): `docker compose down -v`. Si el puerto 5432 ya está ocupado por otro PostgreSQL, páralo antes o cambia el puerto publicado y la `DATABASE_URL`.

### Backend → http://localhost:8000 (documentación: `/docs`)

```bash
cd src/backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend → http://localhost:4200

```bash
cd src/frontend
npm install
npm start
```

## Estructura

```
.
├── src/
│   ├── frontend/        # Angular
│   └── backend/         # FastAPI
├── docs/                # documentación del proyecto
└── .claude/             # material de trabajo del asistente de desarrollo
```

- **`docs/`** es para cualquier lector: el enunciado, las reglas de negocio acordadas, los apuntes con las decisiones de negocio, los diagramas de clases y de base de datos, y las decisiones técnicas con su porqué.
- **`.claude/`** es el material de trabajo de Claude Code, el asistente usado durante el desarrollo: el contexto que necesita cada agente, los planes de implementación y las notas para retomar el trabajo entre sesiones. No hace falta leerlo para entender el proyecto.
