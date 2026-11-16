# 0006 · Idioma del código

Estado: aceptada
Tipo: decisión

## Contexto
El modelo y las reglas de negocio están en español. El código tiene que leerse igual que la documentación.

## Decisión
El dominio va en español (clases, atributos, tablas, endpoints: `Reserva`, `titular`, `/recursos`). Los nombres de las capas y los términos técnicos van en inglés (`controller`, `service`, `repository`, `entity`, `dto`).

## Alternativas descartadas
- Todo en inglés: obliga a traducir cada término entre la documentación y el código.
