// Réplica del contrato de GET /usuarios (decisión 0008): mismos nombres de campo.
import { Rol } from '../common/enums';

export interface Usuario {
  id: number;
  nombre: string;
  apellidos: string;
  rol: Rol;
}

export function esResponsable(usuario: Usuario | null | undefined): boolean {
  return usuario?.rol === 'RESPONSABLE';
}

export function nombreCompleto(usuario: Usuario): string {
  return `${usuario.nombre} ${usuario.apellidos}`;
}
