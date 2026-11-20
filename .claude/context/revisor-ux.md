# Contexto · revisor-ux

## Usuarios y tareas
Trabajadores y responsables, en el navegador de escritorio. No hay login: un selector de usuario permite cambiar de rol.
Tareas, por frecuencia: consultar recursos y su disponibilidad, reservar, aprobar o rechazar (responsable), cancelar o transferir.

## Sistema de diseño
- Decisión 0010: SCSS por componente y variables CSS en `src/styles.scss` (colores, espacios, radios, sombra, fuente). Referencia visual: la web de app2u (azul `#3aabe3`, azul oscuro `#006b98`, Inter, tarjetas con radio de 12px y sombra suave).
- Sin librerías de componentes ni Tailwind. Usar las variables, no valores sueltos.
- Patrones existentes: tarjeta de recurso (`app/recursos/recurso-card`), filtro en píldoras con `aria-current` y estados de carga, error con «Reintentar» y vacío (`app/recursos/recursos.page.html`).
- Reservas: rutas `/recursos/:id?mes&fecha` (detalle con calendario; con `fecha`, modal abierto) y `/reservas?pestana=activas|pasadas|por-aprobar`. Modales con `app/common/dialogo` (`<dialog>` nativo). Colores de estado `--color-pendiente`, `--color-aprobada` (con sus `-fondo`), `--color-ocupado` y `--color-libre`; botones `.boton-secundario` y `.boton-peligro` sobre el `button` global.

## Cómo ver la UI
`docker compose up -d` en la raíz, el backend con `python -m app.seed` y `uvicorn`, y `npm start` en `src/frontend` → http://localhost:4200/recursos. En el devcontainer no hay navegador: la parte visual la comprueba el usuario en local.

## Gotchas
- `--color-marca` (`#3aabe3`) no llega a AA con texto: solo decoración. Para texto, botones y estados activos, `--color-marca-oscuro` (`#006b98`, 5,9:1). Los colores de tipo ya cumplen AA (decisión 0010).
- «Saltar al contenido» mueve el foco con `(click)`: un `href="#…"` con el router navegaría a `/#…` y perdería la URL.
