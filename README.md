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

La versión mínima de Node la impone Angular 22. Los ficheros de versión permiten que los gestores seleccionen la versión correcta automáticamente:

```bash
nvm install                      # instala y activa la versión de .nvmrc
pyenv install --skip-existing    # instala la versión de .python-version
```

> pyenv activa la versión al entrar en el directorio. Con nvm, en cada terminal nueva hay que ejecutar `nvm use`, salvo que tengas configurado el cambio automático.

## Ejecución

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
└── docs/                # enunciado, apuntes, reglas de negocio y diagramas
```
