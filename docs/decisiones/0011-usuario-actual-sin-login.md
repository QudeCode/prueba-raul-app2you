# 0011 · Usuario actual sin login

Estado: aceptada
Tipo: decisión

## Contexto
Las reglas dependen de quién actúa: un trabajador crea reservas pendientes y un responsable, aprobadas (regla 7); solo un responsable aprueba o rechaza (regla 9), y solo el titular cancela o transfiere (regla 13). El enunciado no pide autenticación, pero la API y la interfaz necesitan saber quién es el usuario actual.

## Decisión
- **La API identifica al usuario por la cabecera `X-Usuario-Id`.** La dependencia `get_usuario_actual` (en `usuarios/controller.py`, alias `UsuarioActual`) la lee y devuelve el `UsuarioRespuesta`. Sin cabecera, FastAPI responde 422 como con cualquier parámetro obligatorio. Con un id que no existe, `UsuarioService.obtener_actual` lanza el error del dominio `NoAutenticado`, que el manejador único traduce a **401** (decisión 0012). Un 404 se confundiría con «recurso no encontrado».
- **Solo la exigen los endpoints que dependen de quién llama:** crear, aprobar, rechazar, cancelar, transferir, `mias` y `pendientes`. La disponibilidad es pública.
- **En el frontend, el usuario se elige en un selector de la cabecera.** `UsuariosService` guarda el id elegido en `localStorage` (`reservas.usuarioId`), porque es estado de la sesión y no de la vista (decisión 0009). Sin una elección válida, se toma el primer usuario. `App` es el contenedor del selector, que es presentacional.
- **`ReservasService` pone la cabecera en cada petición, sin interceptor.** Las peticiones de `httpResource` que dependen del usuario (`mias` y `pendientes`) leen el signal del usuario actual, así que se vuelven a pedir al cambiarlo.

## Alternativas descartadas
- Login con contraseña o token: fuera del enunciado, y añade pantallas y almacenamiento de credenciales sin valor para la prueba.
- Un interceptor HTTP que añada la cabecera: esconde la dependencia reactiva del usuario, que las peticiones tendrían que leer igualmente para recargarse.
- El usuario en la URL (`?usuario=`): mezcla la identidad con el estado de la vista y se pierde al seguir enlaces.

## Consecuencias
- Cualquiera puede actuar como cualquier usuario: es una simplificación de la prueba, no un mecanismo de seguridad.
- La cabecera aparece en Swagger (`/docs`) como parámetro obligatorio de los endpoints de reservas.
- El CORS del backend tiene que permitir la cabecera `X-Usuario-Id` y el método `POST`, o el navegador bloquea las peticiones aunque `curl` funcione.
- Con un login real, solo cambiaría `get_usuario_actual` (y la forma de enviar la credencial): los servicios reciben ya el usuario resuelto.
