# 0008 · Arquitectura del frontend: funcionalidades con capas ligeras

Estado: aceptada
Tipo: ADR

## Contexto
El frontend en Angular 22 empieza con su primera pantalla real, el listado de recursos, y después llegarán la disponibilidad y las reservas, que comparten parte del modelo con los recursos. Hace falta fijar cómo se organiza el código, en qué capas se reparte, hacia dónde van las dependencias y cómo se piden los datos.

La prueba valora «un bon anàlisi del problema, un modelat acurat i una implementació neta i ben estructurada» y pide no perder tiempo en configuraciones complejas. La arquitectura tiene que ser clara y defendible sin añadir infraestructura que este tamaño no necesita.

## Decisión

### Organización por funcionalidad
Cada funcionalidad tiene su carpeta con todo lo suyo (`app/recursos/`, más adelante `app/reservas/`), y lo común va en `app/common/`. Es lo que recomienda la guía de estilo oficial de Angular (angular.dev/style-guide: «Organize your project by feature areas» y «Avoid creating subdirectories based on the type of code»). Los ficheros se llaman como su clase, sin sufijo de tipo (`recurso-card.ts` → `RecursoCard`), como en la propia plantilla (`app.ts` → `App`).

```
src/app/
├── common/          enums del dominio con sus etiquetas, URL de la API
├── recursos/        página, componentes, servicio de datos y modelo
└── reservas/        (futuro) igual que recursos
```

### Dos capas de llamadas y un modelo compartido
Tiene la misma forma que el backend (decisión 0001) y la dibuja `docs/diagramas/arquitectura.puml`. Hay que distinguir dos cosas:

**La cadena de llamadas,** donde cada capa solo llama a la siguiente:

| Capa | Qué contiene | Llama a |
|---|---|---|
| Presentación | **Páginas contenedoras** (`recursos.page`): leen la URL, piden los datos al servicio y deciden qué estado mostrar. **Componentes presentacionales** (`recurso-card`): solo `input` y `output`. | Datos |
| Datos | **Un servicio por funcionalidad** (`recursos.service`), el único que conoce la API: URL, parámetros y `httpResource`. | la API (controller del backend) |

En el backend la cadena sigue: controller → service → repository → base de datos, a través de la sesión de `get_session`.

**El modelo,** que no es una capa de la cadena, sino el vocabulario que comparten las capas: los tipos que replican el contrato (`recurso.model`), los enums del dominio con sus etiquetas (`common/enums`) y, cuando haga falta, las reglas en funciones puras, sin Angular. Presentación y Datos lo usan directamente. Si tuviera que pasar capa a capa, el servicio tendría que reexportar tipos y etiquetas sin aportar nada. En el backend tienen ese papel los DTO, las entidades y `common/enums.py`.

Reglas:
- Ninguna capa llama a otra saltándose la intermedia: un componente presentacional nunca inyecta servicios ni hace peticiones, y una página nunca usa `HttpClient`, sino el servicio de su funcionalidad.
- El modelo no depende de nada: ni de Angular ni de las capas que lo usan.
- La lógica de negocio que replique el frontend (por ejemplo, si una reserva se puede cancelar según su política) va en funciones puras del modelo, no en los componentes. El backend sigue siendo la autoridad: la interfaz solo evita ofrecer acciones que la API rechazaría.
- Entre funcionalidades, las dependencias van en una sola dirección, la misma que en el backend: `reservas` puede usar el modelo de `recursos`, nunca al revés. Todas pueden usar `common`.
- Lo que comparte más de una funcionalidad sube a `common/`. Los enums del dominio y sus etiquetas viven en `common/enums.ts`, como `app/common/enums.py` en el backend.

### Datos y estado
- **Componentes `standalone` con signals** (`input`, `computed`). No hay librería de estado: el servicio de cada funcionalidad construye sus peticiones con `httpResource`, que ya expone `value()`, `isLoading()` y `error()` como signals. La lista de un `httpResource` se lee solo si `hasValue()`, porque en Angular 22 `value()` lanza una excepción en estado de error.
- **HTTP con `HttpClient`** (`withFetch`) y la URL base de la API en un único sitio (`common/api.ts`). Las llamadas van directas a `http://localhost:8000`, con el CORS del backend para `localhost:4200`.
- **El modelo replica el contrato de la API:** mismos nombres de campo (`snake_case`) y la misma unión discriminada por `tipo`. Las etiquetas para la interfaz se tipan sobre la lista de valores (`TIPOS_RECURSO as const`), para que no se desincronicen.
- **Estados de carga, error y vacío** en cada vista que pide datos.
- **Comprobación estricta de tipos:** `strict` en TypeScript y `strictTemplates` en Angular, para que la compilación revise también las plantillas.

## Alternativas descartadas
- **Carpetas por tipo** (`views/`, `components/`, `services/`): fue lo habitual en Angular y es la más conocida, pero reparte cada funcionalidad entre varias carpetas, crece mal y no ordena las dependencias. La guía actual la desaconseja.
- **Arquitectura limpia o hexagonal** (casos de uso, puertos como interfaces y adaptadores inyectados por token): aísla el dominio por completo y permite cambiar la API por un mock sin tocar nada más, pero exige una interfaz, un adaptador y una clase de caso de uso por operación, y con un único backend real esas abstracciones no tendrían una segunda implementación. Se conserva lo esencial: reglas en funciones puras y un único punto que conoce la API.
- **Store global con NgRx** (acciones, reducers, effects, selectors): es predecible y tiene herramientas de depuración, pero es la opción con más código repetitivo y se justifica cuando muchas vistas comparten y modifican el mismo estado, que no es el caso.
- **Fachadas por funcionalidad:** permiten cambiar la gestión del estado sin tocar los componentes, pero son una capa más que solo compensa si ese cambio se espera.
- **Monorepo con Nx y límites de dependencia, o micro-frontends:** pensados para equipos y despliegues independientes; aquí serían infraestructura sin uso.
- **Un cliente HTTP propio sobre `fetch`:** Angular ya trae `HttpClient`.
- **Un proxy de desarrollo** (`/api` en `ng serve`): se probó y complicaba la puesta en marcha más que el CORS.
- **Mapear el contrato a `camelCase`:** añade una capa de traducción sin aportar nada.

## Consecuencias
- Una funcionalidad nueva repite la forma de `app/recursos/`, y se ve de un vistazo qué incluye.
- Si el contrato de la API cambia, el modelo del frontend cambia igual.
- La arquitectura por capas de que hablan esta decisión y la 0001 se ve en `docs/diagramas/arquitectura.puml`.
- Las reglas de dependencia se cumplen por revisión (el contexto de los agentes las recoge), no por una herramienta.
- **Cómo crecer, si hace falta:**
  - estado compartido complejo entre vistas → un SignalStore de NgRx por funcionalidad;
  - dos fuentes de datos (API real y mock) → el servicio de datos pasa a ser un puerto, un token de inyección con dos implementaciones, sin tocar páginas ni componentes;
  - hacer cumplir las dependencias automáticamente → reglas de lint de límites entre carpetas.
