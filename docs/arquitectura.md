# Arquitectura

Vista reducida de cómo está construida la aplicación: qué capas hay, para qué sirve cada una y por qué se comunican como lo hacen. El detalle de los componentes de cada capa está en [diagramas/arquitectura.puml](diagramas/arquitectura.puml); esta vista, en [diagramas/arquitectura_capas.puml](diagramas/arquitectura_capas.puml).

La aplicación es un monolito con dos partes, un frontend en Angular y un backend en FastAPI, y una base de datos PostgreSQL (decisiones [0001](decisiones/0001-monolito-modular-por-capas.md), [0002](decisiones/0002-fastapi-sqlalchemy-pydantic.md) y [0007](decisiones/0007-postgresql-docker-compose.md)). Las dos partes tienen la misma forma: capas que se llaman en una sola dirección, cada una solo a la siguiente, y un modelo que comparten todas ([0008](decisiones/0008-estructura-y-datos-del-frontend.md)).

## Capas

### Frontend

| Capa | Propósito | Qué contiene |
|---|---|---|
| **Presentación** | Mostrar el estado y recoger lo que hace el usuario. Las páginas leen la URL y deciden qué mostrar; los componentes solo reciben datos (`input`) y avisan de lo que pasa (`output`). | Páginas (`*.page.ts`) y componentes presentacionales |
| **Datos** | Ser el único sitio que conoce la API: URLs, parámetros, cabeceras y peticiones. | Un servicio por funcionalidad (`*.service.ts`) |
| **Modelo** | El vocabulario común: los tipos que replican el contrato de la API, los enums con sus etiquetas y las reglas que la interfaz repite para no ofrecer lo que la API rechazaría. No depende de Angular. | `*.model.ts`, `common/enums.ts` y `common/fechas.ts` |

### Backend

| Capa | Propósito | Qué contiene |
|---|---|---|
| **Controller** | Traducir HTTP al dominio y de vuelta: rutas, validación de la forma de la petición, usuario actual y conversión de los errores del dominio en códigos HTTP. Sin reglas de negocio. | `*/controller.py`, la dependencia `UsuarioActual` y el manejador de errores de `main.py` |
| **Service** | Las reglas de negocio: qué se puede reservar, quién puede aprobar, plazos de cancelación, disponibilidad. Lanza errores del dominio sin saber nada de HTTP. | `*/service.py` |
| **Repository** | Leer y guardar en la base de datos. Cada consulta tiene un nombre que dice qué devuelve. | `*/repository.py` |
| **Modelo** | Lo que comparten las capas: los DTO (la forma de la API), las entidades (la forma de las tablas), los enums, las horas en minutos y los errores del dominio. | `*/dto.py`, `*/entity.py` y `common/` |

### Base de datos

PostgreSQL en Docker Compose. Guarda usuarios, recursos y reservas, y protege con `CHECK` lo que una fila sola puede garantizar (decisión [0004](decisiones/0004-enums-y-check.md)). Las reglas que cruzan filas o tablas las aplica el servicio.

## Módulos

Cada módulo es una funcionalidad con sus capas dentro (una carpeta por módulo, en el frontend y en el backend). Entre módulos, las dependencias van en una sola dirección: `reservas` usa `recursos` y `usuarios`, nunca al revés, y todos pueden usar `common`.

| Módulo | Propósito | Frontend | Backend |
|---|---|---|---|
| **common** | Lo que comparten todos los módulos | URL de la API y mensajes de error, enums, fechas, reloj y el diálogo modal | Enums, horas en minutos y errores del dominio |
| **usuarios** | Saber quién es el usuario actual, sin login (decisión [0011](decisiones/0011-usuario-actual-sin-login.md)) | El selector de la cabecera y el usuario elegido | `GET /usuarios` y la dependencia que lee `X-Usuario-Id` |
| **recursos** | El catálogo de salas, vehículos y equipos | El listado con filtro por tipo y la tarjeta de recurso | `GET /recursos` |
| **reservas** | Disponibilidad, creación y gestión de reservas (decisiones [0012](decisiones/0012-api-de-reservas-y-errores.md) y [0013](decisiones/0013-disponibilidad-por-tramos.md)) | El detalle del recurso con calendario y modal de reserva, y la página «Reservas» con sus pestañas | `/disponibilidad` y `/reservas`: consultar, crear, aprobar, rechazar, cancelar y transferir |

`App` (la cabecera con la navegación y el selector de usuario) y `main.py` (la aplicación, el CORS y el manejador de errores) son el punto de entrada de cada parte, no un módulo.

## Comunicaciones

| De | A | Cómo | Por qué |
|---|---|---|---|
| Presentación | Datos | Inyecta el servicio de su módulo | La página no sabe nada de HTTP: pide los datos o la acción y recibe signals con su estado (cargando, error o valor). Si cambia la API, solo cambia el servicio. |
| Presentación y Datos | Modelo | Importan tipos, etiquetas y funciones | Los tipos hacen que la compilación detecte un campo mal escrito o un contrato desalineado. Las reglas en funciones puras dejan la interfaz sin lógica y son fáciles de probar. |
| Datos | Controller | HTTP con JSON y la cabecera `X-Usuario-Id` | Es la frontera entre las dos partes. La cabecera identifica al usuario en cada petición que depende de quién llama, porque no hay sesión. |
| Controller | Service | `Depends` de FastAPI, con DTO y el usuario actual | El controller ya ha validado la forma y resuelto el usuario: el servicio recibe datos limpios y solo aplica reglas. |
| Service | Controller | Errores del dominio (`NoEncontrado`, `Conflicto`…) | El servicio dice qué ha fallado sin hablar de HTTP. Un único manejador lo traduce a 400, 401, 403, 404 o 409, así que todos los errores tienen la misma forma (`{"detail": …}`) y el frontend muestra el mensaje tal cual. |
| Service | Service | Llamada directa | `ReservaService` usa `RecursoService`, `UsuarioService` y `DisponibilidadService` para no repetir reglas: crear una reserva valida el hueco con la misma partición del día que responde a la consulta de disponibilidad. |
| Service | Repository | `Depends`, compartiendo la sesión de la petición | El servicio no escribe SQL. Compartir la sesión hace que el bloqueo de la fila del recurso y el commit cubran toda la operación, y dos reservas simultáneas no pueden ocupar el mismo hueco. |
| Repository | Base de datos | SQL con SQLAlchemy | Es la única capa que habla con PostgreSQL; las entidades describen las tablas. |
| Controller, Service y Repository | Modelo | Importan DTO, entidades, enums y errores | Cada capa usa la forma que le corresponde: el controller, los DTO de la API; el repository, las entidades; el servicio, ambos, porque convierte unas en otros. |
