# 0010 · Estilos con SCSS y variables CSS

Estado: aceptada
Tipo: decisión

## Contexto
La interfaz necesita un aspecto coherente entre pantallas sin dedicarle más tiempo del necesario. La referencia visual es la web de app2u (https://www.app2u.es/es/), la empresa para la que es la prueba.

## Decisión
- Se mantiene el SCSS de la plantilla de Angular.
- Los valores de diseño son variables CSS en `:root` de `src/styles.scss`, tomadas de la web de referencia:
  - azul de marca `#3aabe3` y azul oscuro `#006b98`. El azul claro no llega al contraste AA con texto (2,6:1 sobre blanco), así que solo se usa como decoración (la línea superior). Texto, botones y elementos activos usan el azul oscuro (5,9:1), con hover `#005578`, como hace la propia web en sus títulos;
  - un color por tipo de recurso, todos con contraste AA como texto: sala `#006b98`, vehículo `#0f766e` y equipo `#b45309` (el naranja de la web, `#f5a623`, no llega: 2,0:1);
  - texto `#333` y `#555`, fondo `#f5f9fd`, bordes `#eee` y `#ccc`;
  - fuente Inter, cargada desde Google Fonts. Es lo más simple. En producción se serviría desde la propia aplicación, porque cada visita envía la IP del usuario a Google; para una aplicación interna de prueba se acepta. Tarjetas con radio de 12px y sombra suave, botones con radio de 4px y filtros en píldora;
  - una línea superior con el degradado de marca y etiquetas de sección en mayúsculas.
- `styles.scss` contiene también la base mínima: reset, cuerpo, contenedor, botón, foco visible, el enlace «Saltar al contenido» y `prefers-reduced-motion`. Cada componente lleva sus estilos en su `.scss`, encapsulado.
- Sin frameworks de utilidades ni de componentes (ni Tailwind ni Angular Material) y sin estilos `inline`, salvo valores dinámicos.

## Alternativas descartadas
- CSS plano sin preprocesador: válido, pero la plantilla ya trae SCSS y el anidado ayuda en los componentes.
- Angular Material u otra librería de componentes: impone su propio aspecto, lejos de la referencia.

## Consecuencias
- Cambiar un color o un espacio de toda la aplicación es tocar una variable.
- Un color nuevo para texto se comprueba antes contra AA (4,5:1).
- No se usan el logotipo ni los textos de app2u: solo su paleta y su estilo.
