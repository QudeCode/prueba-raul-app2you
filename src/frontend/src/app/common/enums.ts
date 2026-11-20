// Enums del dominio y sus etiquetas, compartidos por todas las funcionalidades (decisión 0008).
// Mismos valores que app/common/enums.py del backend.

export const TIPOS_RECURSO = ['SALA_REUNION', 'VEHICULO', 'EQUIPO'] as const;
export type TipoRecurso = (typeof TIPOS_RECURSO)[number];

export type PoliticaCancelacion = 'FLEXIBLE' | 'MODERADA' | 'BLOQUEADA';
export type ModalidadReserva = 'POR_HORAS' | 'DIA_COMPLETO' | 'AMBAS';
export type EstadoReserva = 'PENDIENTE' | 'APROBADA' | 'RECHAZADA' | 'CANCELADA';
export type Rol = 'TRABAJADOR' | 'RESPONSABLE';

export const TIPO_RECURSO_LABELS: Record<TipoRecurso, string> = {
  SALA_REUNION: 'Sala de reuniones',
  VEHICULO: 'Vehículo',
  EQUIPO: 'Equipo',
};

export const TIPO_RECURSO_PLURAL: Record<TipoRecurso, string> = {
  SALA_REUNION: 'Salas',
  VEHICULO: 'Vehículos',
  EQUIPO: 'Equipos',
};

export const POLITICA_CANCELACION_LABELS: Record<PoliticaCancelacion, string> = {
  FLEXIBLE: 'Flexible',
  MODERADA: 'Moderada',
  BLOQUEADA: 'Bloqueada',
};

export const MODALIDAD_RESERVA_LABELS: Record<ModalidadReserva, string> = {
  POR_HORAS: 'Por horas',
  DIA_COMPLETO: 'Día completo',
  AMBAS: 'Por horas o día completo',
};

export const ESTADO_RESERVA_LABELS: Record<EstadoReserva, string> = {
  PENDIENTE: 'Pendiente',
  APROBADA: 'Aprobada',
  RECHAZADA: 'Rechazada',
  CANCELADA: 'Cancelada',
};

export const ROL_LABELS: Record<Rol, string> = {
  TRABAJADOR: 'Trabajador',
  RESPONSABLE: 'Responsable',
};

export function esTipoRecurso(valor: string | undefined): valor is TipoRecurso {
  return (TIPOS_RECURSO as readonly string[]).includes(valor ?? '');
}
