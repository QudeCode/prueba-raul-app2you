import { HttpErrorResponse } from '@angular/common/http';

/** URL base de la API (decisión 0008): el backend de desarrollo, con CORS para localhost:4200. */
export const API_URL = 'http://localhost:8000';

/** Mensaje para mostrar de un error de la API: su `detail` (decisión 0012) o uno genérico. */
export function mensajeDeError(error: unknown): string {
  if (error instanceof HttpErrorResponse) {
    if (error.status === 0) {
      return 'No se pudo conectar con el backend.';
    }
    const detalle: unknown = error.error?.detail;
    if (typeof detalle === 'string') {
      return detalle;
    }
    return `Error inesperado (código ${error.status}).`;
  }
  return error instanceof Error ? error.message : 'Error inesperado.';
}
