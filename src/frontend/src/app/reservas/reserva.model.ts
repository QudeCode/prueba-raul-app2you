// Réplica del contrato de reservas y disponibilidad (decisión 0008) y las reglas que el frontend
// repite para no ofrecer lo que la API rechazaría. El backend es la autoridad. Sin Angular: el
// «ahora» entra siempre como parámetro.
import { EstadoReserva, ModalidadReserva } from '../common/enums';
import { claveDia } from '../common/fechas';
import { Recurso } from '../recursos/recurso.model';
import { Usuario } from '../usuarios/usuario.model';

export interface Reserva {
  id: number;
  recurso: Recurso;
  titular: Usuario;
  aprobada_por: Usuario | null;
  fecha: string;
  hora_inicio: string | null;
  hora_fin: string | null;
  asistentes_sala: number | null;
  estado: EstadoReserva;
  creada_en: string;
}

export interface Franja {
  inicio: string;
  fin: string;
  libre: boolean;
  capacidad_libre: number | null;
}

export interface Disponibilidad {
  recurso_id: number;
  fecha: string;
  reservas: Reserva[];
  /** `null` si el recurso no admite reservas por horas. */
  franjas: Franja[] | null;
  /** `null` si el recurso no admite día completo. */
  dia_completo_libre: boolean | null;
}

export interface DiaOcupado {
  fecha: string;
  reservas: number;
}

export type Modalidad = Exclude<ModalidadReserva, 'AMBAS'>;

/** «09:00–10:30» o «Todo el día». */
export function textoHoras(reserva: Reserva): string {
  return reserva.hora_inicio && reserva.hora_fin
    ? `${reserva.hora_inicio}–${reserva.hora_fin}`
    : 'Todo el día';
}

export function modalidadesDe(recurso: Recurso): Modalidad[] {
  switch (recurso.modalidad_reserva) {
    case 'POR_HORAS':
      return ['POR_HORAS'];
    case 'DIA_COMPLETO':
      return ['DIA_COMPLETO'];
    case 'AMBAS':
      return ['POR_HORAS', 'DIA_COMPLETO'];
  }
}

/** El recurso solo admite reservas de día completo (vehículos). */
export function soloDiaCompleto(recurso: Recurso): boolean {
  return modalidadesDe(recurso).every((m) => m === 'DIA_COMPLETO');
}

/** Hoy si el recurso admite por horas; mañana si solo admite día completo. */
export function primerDiaElegible(recurso: Recurso, ahora: Date): string {
  const hoy = new Date(ahora.getFullYear(), ahora.getMonth(), ahora.getDate());
  if (soloDiaCompleto(recurso)) {
    hoy.setDate(hoy.getDate() + 1);
  }
  return claveDia(hoy);
}
