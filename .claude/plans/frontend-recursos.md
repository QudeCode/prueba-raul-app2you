# Frontend · Listado de recursos (y decisiones del frontend)

## Contexto
El backend ofrece `GET /recursos`: 8 recursos ordenados por nombre, con una respuesta distinta para cada `tipo`. Las salas incluyen `capacidad_maxima` y `aforo_compartido`; los vehículos, `matricula` y `plazas`; los equipos, `numero_serie`; y todos los recursos traen `imagen` y `modalidad_reserva`. Antes del plan de reservas, el usuario quiere completar la funcionalidad de punta a punta: la pantalla que lista los recursos, que es el punto 1 del enunciado («llistar tots els recursos en una mateixa llista… nom, descripció, tipus, imatge representativa del tipus i atributs específics»).

El frontend es la plantilla de Angular 22. Ahora solo tiene la comprobación provisional de `app.ts`, que hace un `fetch` a `/usuarios` y `/recursos` y pinta lo que recibe.

El usuario compartió las decisiones de frontend de otro proyecto suyo (React). Se adopta, adaptado a Angular, solo lo útil, y se registra como decisiones del proyecto, igual que se hizo con el backend.

Ha decidido además:
- **Estilos:** se mantiene SCSS.
- **Imágenes:** las aporta él.
- **Listado:** tarjetas con un filtro por tipo guardado en la URL.

## Decisiones (`docs/decisiones/`), sin fechas
Aprobar este plan es aceptarlas, como se hizo con la 0007. Las tres se escriben ya como `aceptada`.

- **0008 · Estructura y datos del frontend** (decisión), en `0008-estructura-y-datos-del-frontend.md`
  - **Organización por dominio,** como en el backend: `app/<dominio>/` contiene la página, los componentes, el servicio y el modelo de ese dominio, y `app/shared/` lo común.
  - **Componentes `standalone` con signals.** Sin librería de estado (ni NgRx ni similares): cada dominio tiene un servicio con `httpResource`, que ya da `value()`, `isLoading()` y `error()` como signals.
  - **HTTP con `HttpClient`,** sin librerías externas, y la URL base de la API en un único sitio (`app/shared/api.ts`). Las llamadas van directas a `http://localhost:8000` con el CORS del backend. El proxy de desarrollo se probó y se descartó por complicar la puesta en marcha.
  - **Un solo modelo por tipo del dominio,** que replica el contrato de la API: mismos nombres de campo (`snake_case`) y la misma unión discriminada por `tipo`. Así no hay capa de traducción. Las etiquetas para la interfaz van en constantes junto al modelo (`TIPO_RECURSO_LABELS`…).
  - **Estados de carga, error y vacío** en cada vista que pide datos.
  - **Alternativas descartadas:**
    - NgRx o una store global: no hay estado compartido que lo justifique;
    - un cliente HTTP propio sobre `fetch`: Angular ya trae `HttpClient`;
    - mapear el contrato a `camelCase`: añade una capa sin aportar nada.
- **0009 · Estado de la vista en la URL y filtrado en el servidor** (decisión), en `0009-estado-en-la-url-y-filtrado-en-servidor.md`
  - **El estado de la vista vive en los parámetros de la URL,** no en el componente: ahora el tipo (`/recursos?tipo=SALA_REUNION`) y, más adelante, la fecha de la disponibilidad. Se lee como `input` del componente (`withComponentInputBinding`), y un valor desconocido se trata como «todos».
  - **El filtro se aplica en el backend:** el parámetro de la URL pasa tal cual a la API (`GET /recursos?tipo=SALA_REUNION`), y cada cambio de filtro hace una petición. `httpResource` cancela la anterior si sigue en curso. Así el frontend no recibe todos los recursos cada vez, y el mismo filtro sirve a cualquier otro cliente de la API.
  - **Alternativa descartada:** pedir el catálogo entero y filtrar en el navegador. Es más simple con 8 recursos, pero transfiere datos que no se muestran y deja el filtro solo en el frontend.
  - **Consecuencias:** las vistas se pueden enlazar y el botón de atrás funciona. El filtro no muestra recuentos por tipo, porque requerirían la lista completa.
- **0010 · Estilos con SCSS y variables CSS** (decisión), en `0010-estilos-scss-y-variables-css.md`
  - Se mantiene el SCSS de la plantilla.
  - Los valores de diseño (colores, espacios, radios, tipografía) son variables CSS en `:root` de `styles.scss`, junto con la base mínima (reset y cuerpo). Cada componente lleva sus estilos en su `.scss`, encapsulado.
  - Sin frameworks de utilidades ni de componentes (ni Tailwind ni Material). Sin estilos `inline`, salvo valores dinámicos.
- **`docs/decisiones/README.md`:** las tres filas nuevas, con el formato de las existentes: `| [0008](0008-estructura-y-datos-del-frontend.md) | Estructura y datos del frontend | aceptada |`.
- La 0008 incluye también la **comprobación estricta de tipos**: `strict: true` en TypeScript y `strictTemplates: true` en Angular. Hoy ninguna de las dos está activa, así que la compilación no comprobaba los tipos de las plantillas. **Lo activo con este plan; si no lo quieres, dímelo al aprobar.**

## Ficheros (`src/frontend/`)

**Imágenes** (las aportas tú): `public/imagenes/recursos/sala.png`, `vehiculo.png` y `equipo.png`, con los nombres que da la API.
- No van en `public/recursos/`, para no compartir ruta con la página `/recursos`.
- El frontend las referencia como `/imagenes/recursos/<imagen>`.

**`tsconfig.json`:** `"strict": true` en `compilerOptions` y `"strictTemplates": true` en `angularCompilerOptions` (decisión 0008). Si el código existente no compila con ellas, se corrige en el mismo paso.

**`src/index.html`:** `lang="es"` y `<title>Reservas</title>`.

**`src/app/shared/api.ts`:** `export const API_URL = 'http://localhost:8000';`

**`src/app/app.config.ts`:**
- `provideHttpClient(withFetch())`;
- `provideRouter(routes, withComponentInputBinding())`.

**`src/app/app.routes.ts`:**
- `''` redirige a `recursos`;
- `recursos` carga `RecursosPage` con `title: 'Recursos · Reservas'`;
- `**` redirige a `recursos`.

**`src/app/app.ts`, `app.html` y `app.scss`:** se retira la comprobación provisional y queda la carcasa de la aplicación.
- `<header>`, con el nombre «Reservas» como enlace a `/recursos`;
- `<main>`, que contiene el `<router-outlet />`.

**`src/app/recursos/recurso.model.ts`**
- `TIPOS_RECURSO = ['SALA_REUNION', 'VEHICULO', 'EQUIPO'] as const`, `TipoRecurso = (typeof TIPOS_RECURSO)[number]`, y las etiquetas tipadas como `Record<TipoRecurso, string>`, para que la lista, el tipo y las etiquetas no puedan desincronizarse.
- Tipos literales: `TipoRecurso`, `PoliticaCancelacion` y `ModalidadReserva`.
- `RecursoComun`, con `id`, `nombre`, `descripcion`, `politica_cancelacion`, `modalidad_reserva` e `imagen`.
- `SalaReunion` (`tipo: 'SALA_REUNION'`, `capacidad_maxima`, `aforo_compartido`), `Vehiculo` (`matricula`, `plazas`) y `Equipo` (`numero_serie`).
- `export type Recurso = SalaReunion | Vehiculo | Equipo`.
- Etiquetas:
  - `TIPO_RECURSO_LABELS` (Sala de reuniones, Vehículo, Equipo);
  - `TIPO_RECURSO_PLURAL` para el filtro (Salas, Vehículos, Equipos);
  - `POLITICA_CANCELACION_LABELS` (Flexible, Moderada, Bloqueada);
  - `MODALIDAD_RESERVA_LABELS` (Por horas, Día completo, Por horas o día completo);
  - `TIPOS_RECURSO`, la lista ordenada para pintar el filtro.

**`src/app/recursos/recursos.service.ts`:** `@Injectable({ providedIn: 'root' })`, con `recursos(tipo: Signal<TipoRecurso | null>): HttpResourceRef<Recurso[] | undefined>`.
- Devuelve `httpResource<Recurso[]>(() => ({ url: \`${API_URL}/recursos\`, params: tipo() ? { tipo: tipo()! } : {} }))`.
- Se llama desde un inicializador de campo de la página, que es contexto de inyección. Cada vez que cambia el signal `tipo`, vuelve a pedir la lista.
- El servicio solo sabe construir la petición. El estado de la petición vive en la página. Se mantiene aunque ahora tenga un único consumidor, porque replica el patrón de un servicio por dominio (0008) y lo reutilizará la disponibilidad.

**`src/app/recursos/recursos.page.ts`, `.html` y `.scss`** (`selector: 'app-recursos-page'`)
- `tipo = input<string>()`, el parámetro `?tipo` de la URL.
- `tipoActivo = computed(...)`: el tipo, si es uno de `TIPOS_RECURSO`, o `null` para «todos».
- `recursos = inject(RecursosService).recursos(this.tipoActivo)`: el backend ya devuelve la lista filtrada.
- **La lista se lee solo con `hasValue()`.** En Angular 22, `value()` lanza una excepción si el recurso está en error, y la vista fallaría en lugar de mostrar «Reintentar». Por eso `visibles = computed(() => recursos.hasValue() ? recursos.value() : [])` es la única lectura.
- «Reintentar» llama a `recursos.reload()`.
- **Plantilla:**
  - `<h1>Recursos</h1>`;
  - **El filtro** (`<nav aria-label="Filtrar por tipo">`), que se pinta siempre:
    - «Todos» con `[queryParams]="{ tipo: null }"`, y uno por cada tipo de `TIPOS_RECURSO` con `{ tipo: t }`. Todos llevan `queryParamsHandling="merge"`, para no borrar otros parámetros de la URL, como la futura fecha;
    - el activo lleva `[attr.aria-current]="tipoActivo() === t ? 'page' : null"` y un estilo distinto. Con un `?tipo=XYZ` desconocido queda marcado «Todos», sin tocar la URL;
  - **los estados, en este orden:**
    1. si hay error, «No se pudieron cargar los recursos. Comprueba que el backend está arrancado.» con un botón «Reintentar» (`role="alert"`), desactivado y con el texto «Reintentando…» mientras `isLoading()`;
    2. si `isLoading() && !hasValue()`, «Cargando recursos…» (`role="status"`). Al cambiar de filtro, `httpResource` descarta la lista anterior, así que este mensaje aparece un instante en cada cambio. Se acepta por simple y queda anotado en la 0009;
    3. si no hay ninguno, «No hay recursos de este tipo.» con un tipo activo, o «No hay recursos.» con «Todos»;
    4. si hay datos, la rejilla `<ul>` de `<li><app-recurso-card [recurso]="r" /></li>`.

**`src/app/recursos/recurso-card/recurso-card.ts`, `.html` y `.scss`:** `selector: 'app-recurso-card'` y `recurso = input.required<Recurso>()`.
- La plantilla empieza con `@let r = recurso();`, porque cada llamada a `recurso()` es distinta y el `@if` no estrecharía el tipo de la siguiente. A partir de ahí se usa `r`.
- El `<article>` lleva `[attr.data-tipo]="r.tipo"`, y el `.scss` colorea la etiqueta de tipo con `[data-tipo='SALA_REUNION']`, `[data-tipo='VEHICULO']` y `[data-tipo='EQUIPO']`.

La tarjeta contiene:
- la imagen `/imagenes/recursos/{{ r.imagen }}`. Lleva `alt=""` porque el tipo ya aparece como texto al lado y repetirlo sería ruido para un lector de pantalla. Tiene un tamaño fijo y `object-fit: contain`;
- el nombre (`<h2>`) y una etiqueta con el tipo (`TIPO_RECURSO_LABELS`);
- la descripción;
- una `<dl>` con la política de cancelación y la modalidad de reserva. En las salas (`@if (r.tipo === 'SALA_REUNION')`, que estrecha el tipo de `r`), además la capacidad máxima («10 personas») y el aforo compartido («Sí» o «No»); en los vehículos, la matrícula y las plazas, y en los equipos, el número de serie.

**`src/styles.scss`:** un reset mínimo, el cuerpo y las variables CSS en `:root`:
- colores: `--color-fondo`, `--color-superficie`, `--color-texto`, `--color-texto-suave`, `--color-borde` y `--color-acento`;
- un color por tipo, para la etiqueta: `--color-tipo-sala`, `--color-tipo-vehiculo` y `--color-tipo-equipo`;
- `--espacio-1` a `--espacio-4`, `--radio` y `--fuente` (la fuente del sistema).

**Documentación**
- **`README.md`,** sección Frontend: con el backend arrancado, `npm start` abre el listado de recursos en http://localhost:4200; las imágenes de los tipos van en `public/imagenes/recursos/`. En «Estructura» no cambia nada.
- **`.claude/context/revisor-ux.md`:**
  - en «Sistema de diseño», las variables de `styles.scss`, SCSS por componente, la decisión 0010 y que no hay librerías de componentes;
  - en «Cómo ver la UI», `docker compose up -d`, el backend con el seed y `npm start` en http://localhost:4200/recursos.
- **`.claude/context/implementador.md`,** en «Reutilizar antes de crear»: el patrón del frontend (`app/<dominio>/` con su servicio `httpResource`, su modelo y sus etiquetas; `API_URL`; el estado en la URL).
- **`.claude/plans/frontend-recursos.md`:** este plan, copiado al repo.
- **`.claude/notas/master.md`:** la nueva funcionalidad en curso y el siguiente paso.

## Backend: filtro por tipo en `GET /recursos`
Sigue el patrón de capas del módulo `recursos` (decisión 0001). El CORS para `localhost:4200` ya está.
- **`app/recursos/controller.py`:** `listar(service, tipo: TipoRecurso | None = None)`. FastAPI lo lee del query string, lo valida contra el enum (un valor desconocido da 422 con el detalle) y Swagger muestra el desplegable con los tres valores.
- **`app/recursos/service.py`:** `listar(tipo: TipoRecurso | None = None)` pasa el tipo al repository; la conversión a DTO no cambia.
- **`app/recursos/repository.py`:** `listar(tipo: TipoRecurso | None = None)`. Si llega `tipo`, añade `.where(Recurso.tipo == tipo)`; el orden por nombre e id se mantiene.
- **`.claude/plans/backend-bd-estructura.md`,** en el módulo `recursos`: se anota el parámetro `tipo`.

## Verificación
0. Con el backend parado, compruebo que `value()` lanza una excepción en error, que es lo que justifica leer siempre con `hasValue()`.
1. **Formato y compilación:** Prettier en los ficheros nuevos y `npm run build` en la copia del frontend del scratchpad, con su propio `npm ci`, porque `node_modules` es el de la máquina local. Con `strictTemplates` activo, la compilación comprueba también los tipos de las plantillas: el estrechamiento por `tipo` con `@let` y que `capacidad_maxima` solo se lee en salas.
2. **Backend** (venv propio, copia de `app/` y `DATABASE_URL` de Compose):
   - `GET /recursos` devuelve 8;
   - `?tipo=SALA_REUNION` devuelve las 3 salas, `?tipo=VEHICULO` 2 y `?tipo=EQUIPO` 3, todas ordenadas por nombre;
   - `?tipo=XYZ` da 422;
   - en `/openapi.json`, `tipo` es un parámetro de query opcional con el enum.
3. **De punta a punta en el contenedor:**
   - arranco el backend contra Compose y `ng serve`, los dos desde copias del scratchpad;
   - compruebo que `GET /recursos`, enviado con la cabecera `Origin: http://localhost:4200`, devuelve `access-control-allow-origin: http://localhost:4200`;
   - compruebo que `http://localhost:4200/recursos?tipo=VEHICULO` sirve la aplicación;
   - no hay navegador en el contenedor, así que la parte visual la compruebas tú.
4. **Tú, en local,** con las imágenes en su sitio (y en la pestaña de red, una petición `GET /recursos?tipo=…` por cada cambio de filtro):
   - el listado muestra 8 tarjetas ordenadas por nombre, y las salas con capacidad y aforo;
   - el filtro cambia la URL, y recargar o volver atrás mantiene el filtro;
   - `?tipo=XYZ` muestra todos;
   - con el backend parado, aparece el error con «Reintentar».
5. **Revisión:** `dev:revisar-cambios` con `ui: true`, para que entre el revisor de UX. Sin commit hasta tu aprobación.

## Cambios durante la implementación
- **Referencia visual:** a petición del usuario, los estilos toman como referencia la web de app2u. De su CSS salen el azul `#3aabe3` (hover `#2990c8`), el azul oscuro `#006b98`, Inter, los radios (12px en tarjetas, 4px en botones, 25px en píldoras), la sombra suave y la línea superior con degradado. Queda recogido en la decisión 0010; no se usan su logotipo ni sus textos.
- **Imágenes:** el usuario las aportó como zip de noattributionicons.com (licencia sin atribución; prohíbe redistribuir los iconos sueltos). Se extrajeron los PNG de 512 px como `sala.png`, `vehiculo.png` y `equipo.png`; los zip no van al repo.
- **Servicio:** `params` se declara como `Record<string, string>`, porque el literal condicional no encajaba con el tipo de `httpResource` en modo estricto.
- **Inter** se carga desde Google Fonts en `index.html`.
- **Arquitectura (a petición del usuario):** la 0008 pasa a ser un ADR, «Arquitectura del frontend: funcionalidades con capas ligeras». Recoge tres capas (presentación, datos y dominio), las reglas de dependencia y las alternativas valoradas: carpetas por tipo, arquitectura limpia o hexagonal, NgRx, fachadas y Nx/micro-frontends. También deja escrito cómo crecer si hace falta.
- **`common/`:** `shared/` pasa a llamarse `common/`, como en el backend. Los enums del dominio y sus etiquetas salen de `recurso.model.ts` a `common/enums.ts`, que añade `EstadoReserva` y `Rol` para las reservas. `recurso.model.ts` se queda solo con las interfaces del recurso.
- **Revisión (`dev:revisar-cambios` con UX):** el usuario quitó los zip de `public/`. Se aplicaron:
  - contraste AA: el azul claro solo como decoración; el azul oscuro para texto, botones y la píldora activa; colores de tipo con AA;
  - `--color-sobre-marca`;
  - `role="status"` en el estado vacío;
  - «Saltar al contenido», con `(click)` y foco, sin navegar;
  - píldoras de 44 px y `prefers-reduced-motion`.

  Inter se queda en Google Fonts, anotado en la 0010. Quedan diferidos: `.boton` con variantes, un único sitio para el color por tipo y un título por ruta.
- **Filtrado en el cliente (a petición del usuario):** con «Todos» por defecto, la primera carga ya trae el catálogo entero, así que filtrar en el servidor en cada cambio solo añadía peticiones y un parpadeo de «Cargando…». El servicio vuelve a pedir el catálogo una vez (un `httpResource` compartido), y la página filtra con `computed` y muestra recuentos («Salas (3)»). El backend conserva `?tipo=` como parte de la API. La 0009 pasa a ser «Estado de la vista en la URL y filtrado en el cliente» (`0009-estado-en-la-url-y-filtrado-en-cliente.md`) y recoge la alternativa probada y descartada.
