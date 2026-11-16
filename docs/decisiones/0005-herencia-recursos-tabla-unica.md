# 0005 · Herencia de recursos en una sola tabla

Estado: aceptada
Tipo: decisión

## Contexto
Hay tres tipos de recurso (sala de reunión, vehículo, equipo), cada uno con pocos atributos propios: la sala, la capacidad máxima y el aforo compartido; el vehículo, la matrícula y las plazas; el equipo, el número de serie. La modalidad de reserva y la imagen son fijas para cada tipo.

## Decisión
Se usa una sola tabla `recurso` con la columna discriminadora `tipo` (herencia de tabla única de SQLAlchemy). Los campos propios de cada tipo pueden ir vacíos y un `CHECK` obliga a que cada tipo tenga los suyos rellenos y los ajenos vacíos. La matrícula y el número de serie son únicos. `MODALIDAD_RESERVA` e `IMAGEN` son constantes de clase, no columnas. Las imágenes son ficheros fijos del frontend y la API devuelve su nombre.

## Alternativas descartadas
- Una tabla por tipo: uniones entre tablas para dos campos propios como mucho.
- Una tabla `tipo_recurso`: guarda datos que no cambian nunca y repite lo que ya dicen las clases.

## Consecuencias
- Listar todos los recursos es una sola consulta.
- Un tipo nuevo con muchos campos propios haría replantear esta decisión.
