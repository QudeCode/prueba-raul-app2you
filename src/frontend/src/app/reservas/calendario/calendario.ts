import { Component, computed, input, output } from '@angular/core';
import { formatoDiaLargo, formatoMes, semanasDelMes, sumarMeses } from '../../common/fechas';

/** Mes en rejilla de lunes a domingo, con el recuento de reservas de cada día. */
@Component({
  selector: 'app-calendario',
  templateUrl: './calendario.html',
  styleUrl: './calendario.scss',
})
export class Calendario {
  /** `YYYY-MM`. */
  readonly mes = input.required<string>();
  readonly conteos = input<Record<string, number>>({});
  readonly seleccionada = input<string | null>(null);
  /** «Libre» u «Ocupado» en lugar del recuento (recursos que solo admiten día completo). */
  readonly marcarLibre = input(false);
  /** Los días anteriores no se pueden reservar ni abrir; siguen mostrando su ocupación. */
  readonly primerDiaElegible = input.required<string>();
  readonly compacto = input(false);

  readonly elegir = output<string>();
  readonly cambiarMes = output<string>();

  protected readonly cabeceraDias = ['L', 'M', 'X', 'J', 'V', 'S', 'D'];
  protected readonly semanas = computed(() => semanasDelMes(this.mes()));
  protected readonly titulo = computed(() => formatoMes(this.mes()));
  protected readonly anterior = computed(() => sumarMeses(this.mes(), -1));
  protected readonly siguiente = computed(() => sumarMeses(this.mes(), 1));

  protected numero(dia: string): number {
    return Number(dia.slice(8));
  }

  protected conteo(dia: string): number {
    return this.conteos()[dia] ?? 0;
  }

  protected pasado(dia: string): boolean {
    return dia < this.primerDiaElegible();
  }

  protected resumen(dia: string): string {
    const n = this.conteo(dia);
    if (this.marcarLibre()) {
      return n === 0 ? 'Libre' : 'Ocupado';
    }
    return n === 0 ? '' : `${n} res.`;
  }

  protected etiqueta(dia: string): string {
    const n = this.conteo(dia);
    const fecha = formatoDiaLargo(dia);
    if (this.marcarLibre()) {
      return `${fecha}: ${n === 0 ? 'libre' : 'ocupado'}`;
    }
    return `${fecha}: ${n === 0 ? 'sin reservas' : n === 1 ? '1 reserva' : `${n} reservas`}`;
  }
}
