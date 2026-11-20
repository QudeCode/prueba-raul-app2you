# 0012 · API de reservas y errores del dominio

Estado: aceptada · la ruta de la disponibilidad, sustituida por 0015
Tipo: decisión

## Contexto
Las reservas añaden operaciones que no son un CRUD: crear con validación de conflictos, aprobar, rechazar, cancelar, transferir y consultar la disponibilidad. Cada una puede fallar por motivos distintos (no existe, no tienes permiso, la petición incumple una regla, choca con el estado actual), y el frontend tiene que poder mostrar el motivo.

## Decisión
- **Las acciones son `POST /reservas/{id}/<acción>`** (`aprobar`, `rechazar`, `cancelar`, `transferir`). Son transiciones de estado no idempotentes: repetirlas da 409.
- **La disponibilidad va en `/disponibilidad`** (`GET /disponibilidad?recurso_id&fecha` y `GET /disponibilidad/mes?recurso_id&anio&mes`), con su propio router en el módulo de reservas: es un cálculo sobre las reservas, y así `recursos` no depende de `reservas`.
- **Un único DTO de reserva, `ReservaRespuesta`,** que reutiliza `RecursoRespuesta` y `UsuarioRespuesta` e incluye `puede_cancelar` y `puede_transferir`, calculados en el backend con el reloj del servidor (decisión 0013).
- **La modalidad se deduce de las horas:** con `hora_inicio` y `hora_fin`, por horas; sin ninguna, día completo; con solo una, 400. La tabla no tiene columna de modalidad, y un campo `modalidad` en la petición obligaría a validar que coincide con las horas.
- **Horas en minutos (regla 2):** el tipo `HoraMinuto` (`common/horas.py`) rechaza segundos, microsegundos y zona horaria (422) y se serializa como `"HH:MM"`. En la base, el `CHECK ck_reserva_horas_en_minutos`.
- **Errores del dominio sin HTTP:** `common/errores.py` define `ErrorDominio` y sus subclases. Los servicios los lanzan y un único manejador en `main.py` los traduce, con el cuerpo `{"detail": "<mensaje>"}`, la misma forma que `HTTPException`:

| Error | Código | Cuándo |
|---|---|---|
| `NoEncontrado` | 404 | recurso, reserva o usuario destino que no existe |
| `NoAutenticado` | 401 | `X-Usuario-Id` con un usuario que no existe (decisión 0011) |
| `NoPermitido` | 403 | quien llama no tiene el rol o no es el titular (reglas 9 y 13) |
| `ReglaIncumplida` | 400 | la petición incumple una regla por sí sola (reglas 2, 3, 4 y 18) |
| `Conflicto` | 409 | choca con el estado actual: solapes y aforo (5, 6 y 8), estado de la reserva (9 y 13), plazos (15 y 19) |

  El 422 de FastAPI queda para la forma: tipos, formato de la hora, rangos de `anio` y `mes`, cabecera ausente.
- **Orden de comprobación,** para que el código sea predecible: al crear, 404 del recurso, 400, bloqueo y 409; en las acciones, 404 de la reserva (y del usuario destino), 403, 400 y 409.

## Alternativas descartadas
- `PUT` o `PATCH` con el estado nuevo en el cuerpo: `PUT` promete un reemplazo idempotente, y un `PATCH` de `estado` obliga a validar transiciones arbitrarias en lugar de acciones con nombre.
- `HTTPException` en los servicios: mezcla HTTP en el dominio y reparte la traducción de códigos.
- Horas como minutos enteros (0–1440) en la API: menos legible en Swagger y en las respuestas; ya se descartó guardarlas así (decisión 0004).

## Consecuencias
- Los mensajes de error están en español y el frontend los muestra tal cual (`detail`).
- Un error del dominio nuevo solo necesita su subclase y una fila en `ESTADO_HTTP`.
- Los apuntes del usuario esbozaban `PUT` para las acciones; manda esta decisión.
- La petición de crear admite `fecha_fin` para las reservas de día completo de varios días (decisión 0018).
