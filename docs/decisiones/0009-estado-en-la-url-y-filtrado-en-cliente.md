# 0009 · Estado de la vista en la URL y filtrado en el cliente

Estado: aceptada
Tipo: decisión

## Contexto
El listado de recursos se filtra por tipo, y la disponibilidad necesitará una fecha. Ese estado tiene que sobrevivir a una recarga, poder enlazarse y respetar el botón de atrás. Además, hay que decidir dónde se filtra: la API admite `GET /recursos?tipo=`, y el listado abre por defecto en «Todos», porque el enunciado pide listar todos los recursos en una misma lista.

## Decisión
- **El estado de la vista vive en los parámetros de la URL,** no en el componente: ahora el tipo (`/recursos?tipo=SALA_REUNION`) y, más adelante, la fecha. La página lo recibe como `input` (`withComponentInputBinding`), y un valor desconocido se trata como «todos». Los enlaces del filtro usan `queryParamsHandling="merge"` para no borrar otros parámetros.
- **El listado pide el catálogo completo una sola vez y filtra en memoria** con `computed`. El servicio comparte esa petición entre visitas a la página.
- **La API conserva `GET /recursos?tipo=`** como parte de su contrato (aparece en Swagger y sirve a cualquier otro cliente), aunque el listado no lo use.

## Alternativas descartadas
- Guardar el filtro en el estado del componente: se pierde al recargar y no se puede enlazar.
- Filtrar en el servidor en cada cambio de filtro: con «Todos» por defecto, la primera carga ya trae el catálogo entero. Volver a pedir al cambiar de tipo descarga un subconjunto de lo que ya se tiene, añade una petición por cambio y muestra un instante «Cargando…». Se probó en esta misma funcionalidad y se descartó por eso.

## Consecuencias
- Las vistas se pueden enlazar, y la recarga y el botón de atrás mantienen el filtro.
- El cambio de filtro es instantáneo, sin peticiones, y el filtro muestra recuentos por tipo («Salas (3)»).
- Si el catálogo creciera tanto que no conviniera pedirlo entero, el listado pasaría a usar `?tipo=` (y a paginar) sin cambiar la API.
