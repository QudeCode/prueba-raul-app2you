# 0002 · FastAPI, SQLAlchemy 2.0 y Pydantic v2

Estado: aceptada
Tipo: decisión

## Contexto
El enunciado permite Python para el backend. Hace falta un framework web, un ORM y una forma de validar peticiones y respuestas.

## Decisión
Se usa FastAPI con SQLAlchemy 2.0 en modo síncrono y Pydantic v2. Las capas se conectan con `Depends`. La sesión de base de datos se abre por petición y no hace commit automático: los servicios que escriben hacen commit de forma explícita, antes de responder.

## Alternativas descartadas
- SQLModel: une DTO y entidad en una sola clase, lo que rompe la separación de la decisión 0001.
- SQLAlchemy asíncrono: más complejidad sin beneficio para este volumen.
- Commit automático al cerrar la sesión: FastAPI puede ejecutarlo después de enviar la respuesta, y un fallo en la base daría un 200 sin guardar nada.

## Consecuencias
- Swagger en `/docs` sale gratis de los DTO.
- Cada servicio que escribe es responsable de su commit.
