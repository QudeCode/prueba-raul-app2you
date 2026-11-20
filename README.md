# Reservas — prueba técnica

Sistema de reservas de recursos empresariales (ver [enunciado](docs/enunciado.md)).

Las reglas de negocio acordadas están en [docs/reglas_negocio.md](docs/reglas_negocio.md), la arquitectura por capas en [docs/arquitectura.md](docs/arquitectura.md) (con los diagramas [reducido](docs/diagramas/arquitectura_capas.puml) y [detallado](docs/diagramas/arquitectura.puml)) y las decisiones técnicas en [docs/decisiones/](docs/decisiones/README.md).

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

### Backend → http://localhost:8000/docs

```bash
cd src/backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app.seed               # crea las tablas y carga los datos de prueba (borra lo que hubiera)
uvicorn app.main:app --reload
```

> El seed necesita la base de datos arrancada y el `.env` copiado (apartado anterior). Carga 4 usuarios, 8 recursos y reservas aleatorias de los próximos 21 días (creadas con las mismas reglas que la API), más unas pocas de los días anteriores. Se puede repetir para volver al estado inicial. Solo actúa sobre una base local: si la `DATABASE_URL` apunta a otra máquina, se niega a borrar nada.

### Frontend → http://localhost:4200

```bash
cd src/frontend
npm install
npm start
```

> Con el backend arrancado, abre el listado de recursos (`/recursos`), con filtro por tipo. Las imágenes de cada tipo están en `src/frontend/public/imagenes/recursos/`.

## Uso

- **Usuario actual:** no hay login. Se elige en el selector de la cabecera: Ana y Luis son trabajadores (sus reservas quedan pendientes) y Marta y Jordi, responsables (las suyas quedan aprobadas y pueden aprobar o rechazar las pendientes).
- **Reservar:** desde una tarjeta de `/recursos` se abre el detalle del recurso con su calendario. En salas y equipos por horas, al elegir un día se abre un modal con el timeline del día; en vehículos (y equipos por día completo), se reservan días enteros: de 1 a 7 seguidos, eligiendo el último día en el modal.
- **Reservas:** las propias y, para un responsable, las pendientes de aprobar, en pestañas «Activas», «Pasadas» y, para un responsable, «Por aprobar». Cancelar y transferir solo aparecen cuando la política del recurso lo permite.
- **API:** en http://localhost:8000/docs. Los principales: `GET /recursos` (y `/recursos/{id}`), `GET /recursos/{id}/disponibilidad?fecha=` (con `&fecha_fin=`, un rango de día completo) y `…/disponibilidad/mes?anio=&mes=`, que son públicos, y `/reservas` (crear, `GET /reservas/{id}`, `mias`, `pendientes` y las acciones `aprobar`, `rechazar`, `cancelar` y `transferir`). Los de reservas piden la cabecera `X-Usuario-Id` con el id del usuario (1 Ana, 2 Luis, 3 Marta, 4 Jordi).

### Probar la API con curl

Con el seed cargado, la Sala Mar es el recurso 1 (aforo compartido de 10). Sustituye `2030-01-15` por una fecha futura.

```bash
# Disponibilidad de la Sala Mar ese día: franjas libres, capacidad libre y reservas que las ocupan
curl "http://localhost:8000/recursos/1/disponibilidad?fecha=2030-01-15"

# Ana (trabajadora, id 1) reserva de 10:00 a 11:00 para 4 personas: queda PENDIENTE
curl -X POST http://localhost:8000/reservas \
  -H "Content-Type: application/json" -H "X-Usuario-Id: 1" \
  -d '{"recurso_id": 1, "fecha": "2030-01-15", "hora_inicio": "10:00", "hora_fin": "11:00", "asistentes_sala": 4}'

# Marta (responsable, id 3) ve las pendientes y aprueba la de Ana (usa el id que devolvió la petición anterior)
curl -H "X-Usuario-Id: 3" http://localhost:8000/reservas/pendientes
curl -X POST -H "X-Usuario-Id: 3" http://localhost:8000/reservas/<id>/aprobar
```

## Estructura

```
.
├── src/
│   ├── frontend/        # Angular
│   └── backend/         # FastAPI
├── docs/                # documentación del proyecto
└── .claude/             # contexto y planes del desarrollo asistido con IA
```

- **`docs/`** es para cualquier lector: el enunciado, las reglas de negocio acordadas, los apuntes con las decisiones de negocio, los diagramas de clases y de base de datos, y las decisiones técnicas con su porqué.
- **`.claude/`** contiene el material del desarrollo asistido con IA (ver el apartado siguiente).

## Uso de IA

El proyecto se ha desarrollado con [Claude Code](https://claude.com/claude-code) como asistente. El análisis del enunciado, las reglas de negocio y las decisiones son míos; la IA ha ayudado a redactar planes, implementar y revisar, y cada cambio ha pasado por mi aprobación antes del commit.

- **`CLAUDE.md`**: las directrices del proyecto para el asistente (comandos, reglas, idioma, documentación y commits).
- **`.claude/context/`**: el contexto de cada agente (planificación, implementación, verificación y revisión de código, de planes y de UX).
- **`.claude/plans/`**: los planes de implementación aprobados, con sus decisiones y tareas.
- **`.claude/notas/`**: el estado del trabajo para retomarlo entre sesiones.
