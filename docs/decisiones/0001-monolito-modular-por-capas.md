# 0001 · Monolito modular con capas controller, service y repository

Estado: aceptada
Tipo: ADR

## Contexto
El backend necesita una estructura clara y predecible para separar HTTP, reglas de negocio y persistencia. Hay tres dominios: usuarios, recursos y reservas.

## Decisión
Se usa una sola aplicación FastAPI dividida en módulos (`usuarios`, `recursos`, `reservas`). Cada módulo tiene un fichero por capa:

| Fichero | Responsabilidad |
|---|---|
| `controller.py` | Endpoints, rutas y validación de la petición |
| `dto.py` | Esquemas Pydantic de petición y respuesta (pertenecen al controller) |
| `service.py` | Reglas de negocio y conversión de entidad a DTO |
| `repository.py` | Acceso a datos y consultas |
| `entity.py` | Entidades SQLAlchemy (pertenecen al repository) |

Reglas:
- El controller no importa entidades; el repository no importa DTO.
- El servicio hace las conversiones en línea, sin clases Mapper, y devuelve DTO.
- Los módulos se comunican llamando a servicios en el mismo proceso.

## Alternativas descartadas
- Microservicios: el tamaño del problema no justifica el coste operativo.
- Una carpeta por capa dentro de cada módulo: con módulos pequeños, cada carpeta tendría un solo fichero.

## Consecuencias
- Todos los módulos tienen los mismos ficheros en el mismo sitio.
- Un servicio que devuelve una entidad al controller, o un controller que importa una entidad, es un error de diseño.
