# 0015 · Rutas REST de recursos, reservas y disponibilidad

Estado: aceptada
Tipo: decisión
Sustituye en parte a: [0012](0012-api-de-reservas-y-errores.md) (la ruta de la disponibilidad)

## Contexto
La API tenía `GET /recursos` y `GET /reservas/mias`, pero no una ruta para un recurso o una reserva concretos, y la disponibilidad colgaba de `/disponibilidad?recurso_id=…`, aunque siempre es la de un recurso.

## Decisión
- **`GET /recursos/{recurso_id}`:** el recurso, o 404.
- **`GET /reservas/{reserva_id}`:** la reserva para su titular o para un responsable (que ve todas porque las aprueba); 403 para otro trabajador y 404 si no existe. Como el resto de `/reservas`, exige `X-Usuario-Id` (decisión 0011). Se declara después de `/reservas/mias` y `/reservas/pendientes`, que si no encajarían en `{reserva_id}`.
- **El 403 no es un control de privacidad:** las reservas activas ya se ven con todos sus datos en la disponibilidad, que es pública. En la práctica solo restringe el detalle de las reservas rechazadas y canceladas de otros.
- **La disponibilidad cuelga del recurso:** `GET /recursos/{recurso_id}/disponibilidad?fecha=` y `GET /recursos/{recurso_id}/disponibilidad/mes?anio=&mes=`. El código sigue en el módulo de reservas (`router_disponibilidad` en `reservas/controller.py`): la URL es del recurso, pero el cálculo es sobre las reservas, y así `recursos` sigue sin depender de `reservas`.
- **Sin rutas antiguas:** `/disponibilidad` y `/disponibilidad/mes` desaparecen. El único cliente es el frontend de este repositorio.
- **El frontend sigue sacando el recurso del catálogo** que ya tiene cargado (decisión 0009): `GET /recursos/{id}` es para otros clientes de la API.

## Alternativas descartadas
- Mantener `/disponibilidad?recurso_id=`: la URL anidada dice de quién es la disponibilidad.
- Llevar los endpoints de disponibilidad a `recursos/controller.py`: haría depender `recursos` de `reservas`.
- `GET /reservas/{id}` sin 403: un trabajador podría leer las reservas cerradas de otros.

## Consecuencias
- La ruta de la disponibilidad de la 0012 queda sustituida; el resto de la 0012 sigue vigente.
- Swagger agrupa la disponibilidad bajo su propia etiqueta, con la URL del recurso.
