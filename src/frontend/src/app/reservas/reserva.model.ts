// Réplica del contrato de reservas y disponibilidad (decisión 0008) y las reglas que el frontend
// repite para no ofrecer lo que la API rechazaría. El backend es la autoridad. Sin Angular: el
// «ahora» entra siempre como parámetro.
import { EstadoReserva, ModalidadReserva } from '../common/enums';
import { claveDia, dos } from '../common/fechas';
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

export interface ReservaNueva {
  recurso_id: number;
  fecha: string;
  hora_inicio: string | null;
  hora_fin: string | null;
  asistentes_sala: number | null;
}

export type Modalidad = Exclude<ModalidadReserva, 'AMBAS'>;
export type Pestana = 'activas' | 'pasadas';

/** Tramo del día en minutos desde las 00:00. */
export interface Seleccion {
  inicio: number;
  fin: number;
}

/** Último minuto reservable (23:59, regla 2). */
export const FIN_DIA = 1439;
/** Ancho del eje del día (00:00 a 24:00). */
export const MINUTOS_DIA = 1440;

export function aMinutos(hora: string): number {
  const [h, m] = hora.split(':').map(Number);
  return h * 60 + m;
}

export function aHora(minutos: number): string {
  return `${dos(Math.floor(minutos / 60))}:${dos(minutos % 60)}`;
}

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

/** Capacidad máxima si es una sala con aforo compartido (varias reservas a la vez); si no, `null`. */
export function capacidadCompartida(recurso: Recurso): number | null {
  return recurso.tipo === 'SALA_REUNION' && recurso.aforo_compartido
    ? recurso.capacidad_maxima
    : null;
}

/** El recurso solo admite reservas de día completo (vehículos). */
export function soloDiaCompleto(recurso: Recurso): boolean {
  return modalidadesDe(recurso).every((m) => m === 'DIA_COMPLETO');
}

export function esActiva(reserva: Reserva): boolean {
  return reserva.estado === 'PENDIENTE' || reserva.estado === 'APROBADA';
}

/** Una reserva de hoy sigue en «activas» todo el día. */
export function pestanaDe(reserva: Reserva, hoy: string): 'activas' | 'pasadas' {
  return esActiva(reserva) && reserva.fecha >= hoy ? 'activas' : 'pasadas';
}

/** Regla 3 con el inicio a las 00:00 en día completo: hoy ya no se puede reservar. */
export function diaReservable(fecha: string, modalidad: Modalidad, ahora: Date): boolean {
  const hoy = claveDia(ahora);
  return modalidad === 'POR_HORAS' ? fecha >= hoy : fecha > hoy;
}

/** Hoy si el recurso admite por horas; mañana si solo admite día completo. */
export function primerDiaElegible(recurso: Recurso, ahora: Date): string {
  const hoy = new Date(ahora.getFullYear(), ahora.getMonth(), ahora.getDate());
  if (soloDiaCompleto(recurso)) {
    hoy.setDate(hoy.getDate() + 1);
  }
  return claveDia(hoy);
}

/** Primer minuto elegible de `fecha`: 0 si es futuro, el siguiente al actual hoy, el final si ya pasó. */
export function primerMinuto(fecha: string, ahora: Date): number {
  const hoy = claveDia(ahora);
  if (fecha > hoy) {
    return 0;
  }
  if (fecha < hoy) {
    return MINUTOS_DIA;
  }
  return Math.min(ahora.getHours() * 60 + ahora.getMinutes() + 1, MINUTOS_DIA);
}

function tramosQueCubre(franjas: Franja[], inicio: number, fin: number): Franja[] {
  return franjas.filter((f) => aMinutos(f.inicio) < fin && aMinutos(f.fin) > inicio);
}

/** Capacidad libre mínima exigida: 1 persona si no se indica. */
function plazasPedidas(asistentes: number | null): number {
  return Math.max(1, asistentes ?? 1);
}

function franjaCabe(franja: Franja, asistentes: number | null): boolean {
  return (
    franja.libre &&
    (franja.capacidad_libre === null || franja.capacidad_libre >= plazasPedidas(asistentes))
  );
}

function tramoLibre(franjas: Franja[], tramo: Seleccion, asistentes: number | null): boolean {
  const cubiertas = tramosQueCubre(franjas, tramo.inicio, tramo.fin);
  return cubiertas.length > 0 && cubiertas.every((f) => franjaCabe(f, asistentes));
}

export interface EntradaMotivo {
  recurso: Recurso;
  modalidad: Modalidad | null;
  fecha: string;
  seleccion: Seleccion | null;
  asistentes: number | null;
  disponibilidad: Disponibilidad | null;
  ahora: Date;
}

/** El primer motivo por el que no se puede reservar, o `null` si se puede. */
export function motivoNoReservable(e: EntradaMotivo): string | null {
  if (e.modalidad === null) {
    return 'Elige si reservas por horas o el día completo.';
  }
  if (!diaReservable(e.fecha, e.modalidad, e.ahora)) {
    return e.fecha < claveDia(e.ahora)
      ? 'Este día ya ha pasado.'
      : 'Un día completo no se puede reservar para hoy.';
  }
  if (e.disponibilidad === null) {
    return 'Esperando la disponibilidad del día.';
  }
  if (e.modalidad === 'DIA_COMPLETO') {
    return e.disponibilidad.dia_completo_libre === false ? 'El día ya está ocupado.' : null;
  }
  const { seleccion, recurso } = e;
  if (seleccion === null) {
    return 'Elige la franja horaria.';
  }
  if (seleccion.fin <= seleccion.inicio) {
    return 'La hora de fin debe ser posterior a la de inicio.';
  }
  if (seleccion.fin > FIN_DIA) {
    return 'La hora de fin máxima es las 23:59.';
  }
  if (seleccion.inicio < primerMinuto(e.fecha, e.ahora)) {
    return 'La hora de inicio ya ha pasado.';
  }
  const capacidad = capacidadCompartida(recurso);
  const aforo = capacidad !== null;
  if (capacidad !== null) {
    const n = e.asistentes;
    if (n === null || !Number.isInteger(n) || n < 1 || n > capacidad) {
      return `Los asistentes deben estar entre 1 y ${capacidad}.`;
    }
  }
  const cubiertas = tramosQueCubre(e.disponibilidad.franjas ?? [], seleccion.inicio, seleccion.fin);
  if (cubiertas.some((f) => !f.libre)) {
    return aforo
      ? 'No queda capacidad en parte de la franja elegida.'
      : 'La franja elegida está ocupada.';
  }
  const sinCapacidad = cubiertas.find((f) => !franjaCabe(f, e.asistentes));
  if (sinCapacidad) {
    return `No hay capacidad suficiente: en parte de la franja solo quedan ${sinCapacidad.capacidad_libre} plazas.`;
  }
  return null;
}

/**
 * Efecto de pulsar una celda de 30 minutos del timeline. Sin selección, la celda; con selección,
 * la unión de las dos si toda ella está libre; si no, la celda sola si está libre; si tampoco, `null`.
 * El `fin` se recorta a `FIN_DIA`, para que la API nunca reciba «24:00».
 */
export function ajustarSeleccion(
  actual: Seleccion | null,
  celda: Seleccion,
  franjas: Franja[],
  asistentes: number | null,
  primerMinutoElegible: number,
): Seleccion | null {
  const sola: Seleccion = { inicio: celda.inicio, fin: Math.min(celda.fin, FIN_DIA) };
  const valida = (tramo: Seleccion) =>
    tramo.inicio >= primerMinutoElegible && tramoLibre(franjas, tramo, asistentes);

  if (actual && actual.fin > actual.inicio) {
    const dentro = sola.inicio >= actual.inicio && sola.fin <= actual.fin;
    const union: Seleccion = {
      inicio: Math.min(actual.inicio, sola.inicio),
      fin: Math.max(actual.fin, sola.fin),
    };
    if (!dentro && valida(union)) {
      return union;
    }
  }
  return valida(sola) ? sola : null;
}
