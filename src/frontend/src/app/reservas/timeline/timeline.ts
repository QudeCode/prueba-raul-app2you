import { Component, computed, input, output } from '@angular/core';
import { ESTADO_RESERVA_LABELS } from '../../common/enums';
import { nombreCompleto } from '../../usuarios/usuario.model';
import { ReservasDelDia } from '../reservas-del-dia/reservas-del-dia';
import {
  aHora,
  aMinutos,
  Franja,
  MINUTOS_DIA,
  rangoMinutos,
  Reserva,
  Seleccion,
  textoHoras,
} from '../reserva.model';

interface Bloque {
  reserva: Reserva;
  izquierda: number;
  ancho: number;
}

interface Segmento {
  franja: Franja;
  izquierda: number;
  ancho: number;
  /** Ocupación de 0 a 1, para la intensidad del color. */
  ocupacion: number;
}

const PASO = 30;

/** Eje de 00:00 a 24:00 con lo ocupado, la selección y celdas de 30 minutos para elegir con el ratón. */
@Component({
  selector: 'app-timeline',
  imports: [ReservasDelDia],
  templateUrl: './timeline.html',
  styleUrl: './timeline.scss',
})
export class Timeline {
  readonly franjas = input<Franja[] | null>(null);
  readonly reservas = input.required<Reserva[]>();
  /** Aforo compartido: se muestran las plazas libres por franja en lugar de un bloque por reserva. */
  readonly aforo = input(false);
  readonly capacidad = input<number | null>(null);
  readonly seleccion = input<Seleccion | null>(null);
  readonly primerMinuto = input(0);

  readonly elegirCelda = output<Seleccion>();

  protected readonly celdas = Array.from({ length: MINUTOS_DIA / PASO }, (_, i) => ({
    inicio: i * PASO,
    fin: (i + 1) * PASO,
  }));
  protected readonly horas = Array.from({ length: 23 }, (_, i) => i + 1);
  protected readonly etiquetas = [0, 3, 6, 9, 12, 15, 18, 21, 24];
  protected readonly nombreCompleto = nombreCompleto;
  protected readonly aHora = aHora;

  protected readonly pasado = computed(() => (this.primerMinuto() / MINUTOS_DIA) * 100);

  protected readonly bloques = computed<Bloque[]>(() =>
    this.reservas().map((reserva) => {
      const [inicio, fin] = rangoMinutos(reserva);
      return { reserva, izquierda: this.porcentaje(inicio), ancho: this.porcentaje(fin - inicio) };
    }),
  );

  protected readonly segmentos = computed<Segmento[]>(() => {
    const capacidad = this.capacidad();
    return (this.franjas() ?? []).map((franja) => {
      const inicio = aMinutos(franja.inicio);
      const fin = aMinutos(franja.fin);
      const libres = franja.capacidad_libre;
      return {
        franja,
        izquierda: this.porcentaje(inicio),
        ancho: this.porcentaje(fin - inicio),
        ocupacion: capacidad && libres !== null ? 1 - libres / capacidad : 0,
      };
    });
  });

  protected readonly marcaSeleccion = computed(() => {
    const s = this.seleccion();
    return s && s.fin > s.inicio
      ? { izquierda: this.porcentaje(s.inicio), ancho: this.porcentaje(s.fin - s.inicio) }
      : null;
  });

  protected porcentaje(minutos: number): number {
    return (minutos / MINUTOS_DIA) * 100;
  }

  protected celdaPasada(celda: Seleccion): boolean {
    return celda.inicio < this.primerMinuto();
  }

  protected textoSegmento(s: Segmento): string {
    const libres = s.franja.capacidad_libre;
    return `${s.franja.inicio}–${s.franja.fin}: ${libres} ${libres === 1 ? 'libre' : 'libres'}`;
  }

  protected textoBloque(b: Bloque): string {
    return `${textoHoras(b.reserva)}: ${nombreCompleto(b.reserva.titular)} (${ESTADO_RESERVA_LABELS[b.reserva.estado]})`;
  }
}
