# Contexto · implementador

## Apps y rutas
- Backend: `src/backend/app/<módulo>/{controller,dto,service,repository,entity}.py` (decisión 0001).
- Frontend: `src/frontend` (Angular 22).

## Skills de stack que cargar
Ninguna: no hay plugin de stack para FastAPI ni Angular.

## Reutilizar antes de crear
- `app/database.py` (`get_session`, `tipo_enum`, `check_enum`, `es_local`, `recrear_esquema`), `app/common/enums.py`, `app/entidades.py`.
- Patrón de capas de `app/usuarios/`: cada capa expone su proveedor para `Depends` junto a su clase (`get_<x>_repository` en `repository.py`, `get_<x>_service` en `service.py`); el controller solo importa el servicio y los DTO. Columnas de enum con `tipo_enum` + `check_enum`.
- `main.py` registra las entidades con `from app import entidades` (no `import app.entidades`: pisaría el nombre `app`).
- Frontend (decisiones 0008 a 0010): una funcionalidad por carpeta como `src/app/recursos/` (página contenedora, componentes presentacionales, servicio de datos con `httpResource`, modelo). Enums del dominio y etiquetas en `src/app/common/enums.ts` y `API_URL` en `src/app/common/api.ts`. Estado de la vista en la URL como `input` de la página; leer un `httpResource` solo con `hasValue()`; variables de `src/styles.scss`. Reglas de negocio del frontend en funciones puras del dominio, no en componentes.
- Backend de reservas (decisiones 0011 a 0013): errores del dominio en `app/common/errores.py` (los traduce el manejador único de `main.py`; nunca `HTTPException` en un servicio), horas con `HoraMinuto` y `INICIO_DIA`/`FIN_DIA` de `app/common/horas.py`, usuario actual con `UsuarioActual` de `usuarios/controller.py`. Los plazos de cancelar y transferir solo en el backend (`puede_cancelar`/`puede_transferir`).
- Frontend de reservas: fechas como claves locales con `src/app/common/fechas.ts`; modales con `src/app/common/dialogo/` (no otro `<dialog>`); cabecera de recurso con `recursos/recurso-cabecera/`; `mensajeDeError` de `common/api.ts`. `reservas` puede usar `recursos` y `usuarios`, nunca al revés (0008).

## No tocar
- `src/backend/.venv` (es el de la máquina local) y cualquier `.env`.

## Cómo verificar lo que implementas
Con un venv propio fuera del repo (`pip install -r src/backend/requirements.txt`) y el PostgreSQL de Docker Compose en `host.docker.internal:5432`. El resultado en la máquina local es el que vale.

## Gotchas
- No añadir tests ni dependencias de test.
- `<dialog>.showModal()` falla si el elemento aún no está en el DOM: se abre en un `effect` sobre un `viewChild` no requerido (con `viewChild.required` el `effect` puede ejecutarse antes de resolver la consulta). Ya lo resuelve `common/dialogo/`.
- `prettier --write` sobre `src` reformatea `index.html` y `main.ts`, que están sin formatear en el repo: exclúyelos.
