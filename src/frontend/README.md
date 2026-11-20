# Frontend

Aplicación Angular del sistema de reservas. Cómo arrancar todo el proyecto (base de datos, backend y frontend): [README raíz](../../README.md).

## Comandos

```bash
npm install      # dependencias
npm start        # servidor de desarrollo → http://localhost:4200 (necesita el backend en :8000)
npm run build    # compilación de producción; comprueba también los tipos de las plantillas
```

## Estructura

Una carpeta por funcionalidad, con sus páginas, componentes, servicio de datos y modelo (decisión [0008](../../docs/decisiones/0008-estructura-y-datos-del-frontend.md)):

```
src/app/
├── common/      URL de la API, enums con sus etiquetas, fechas, reloj y el diálogo compartido
├── usuarios/    usuario actual (sin login) y su selector
├── recursos/    listado de recursos con filtro por tipo
└── reservas/    detalle del recurso con calendario y reserva, y la página «Reservas»
```

Las imágenes de cada tipo de recurso están en `public/imagenes/recursos/`.
