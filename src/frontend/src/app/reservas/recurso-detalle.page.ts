import { Component, computed, inject, input } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { ahoraPorMinuto } from '../common/reloj';
import { claveDia, claveMes, esClaveDia, esClaveMes } from '../common/fechas';
import { RecursoCard } from '../recursos/recurso-card/recurso-card';
import { RecursosService } from '../recursos/recursos.service';
import { Calendario } from './calendario/calendario';
import { primerDiaElegible, soloDiaCompleto } from './reserva.model';
import { ReservasService } from './reservas.service';

@Component({
  selector: 'app-recurso-detalle-page',
  imports: [RouterLink, RecursoCard, Calendario],
  templateUrl: './recurso-detalle.page.html',
  styleUrl: './recurso-detalle.page.scss',
})
export class RecursoDetallePage {
  /** Parámetros de la URL (decisión 0009): `/recursos/:id?mes=YYYY-MM&fecha=YYYY-MM-DD`. */
  readonly id = input<string>();
  readonly mes = input<string>();
  readonly fecha = input<string>();

  private readonly router = inject(Router);
  private readonly reservas = inject(ReservasService);
  protected readonly recursos = inject(RecursosService).recursos;

  /** «Ahora» con precisión de minuto, de donde salen `hoy` y el primer minuto elegible. */
  protected readonly ahora = ahoraPorMinuto();
  private readonly hoy = computed(() => claveDia(this.ahora()));

  protected readonly mesActivo = computed(() => {
    const mes = this.mes();
    const fecha = this.fecha();
    if (esClaveMes(mes)) {
      return mes;
    }
    return esClaveDia(fecha) ? claveMes(fecha) : claveMes(this.hoy());
  });

  /** Día elegido en el calendario (`fecha` válida). */
  protected readonly fechaActiva = computed(() => {
    const fecha = this.fecha();
    return esClaveDia(fecha) ? fecha : null;
  });

  // value() lanza si el recurso está en error: solo se lee con hasValue()
  protected readonly recurso = computed(() => {
    if (!this.recursos.hasValue() || !/^\d+$/.test(this.id() ?? '')) {
      return undefined;
    }
    return this.recursos.value().find((r) => r.id === Number(this.id()));
  });

  private readonly recursoId = computed(() => this.recurso()?.id ?? null);

  protected readonly mesReservas = this.reservas.mes(this.recursoId, this.mesActivo);

  protected readonly conteos = computed(() =>
    this.mesReservas.hasValue()
      ? Object.fromEntries(this.mesReservas.value().map((d) => [d.fecha, d.reservas]))
      : {},
  );

  protected readonly primerDia = computed(() => {
    const r = this.recurso();
    return r ? primerDiaElegible(r, this.ahora()) : this.hoy();
  });

  /** Solo los recursos de día completo muestran «Libre» u «Ocupado» en el calendario. */
  protected readonly marcarLibre = computed(() => {
    const r = this.recurso();
    return r !== undefined && soloDiaCompleto(r);
  });

  protected elegirDia(fecha: string): void {
    this.irA({ fecha, mes: claveMes(fecha) });
  }

  protected cambiarMes(mes: string): void {
    this.irA({ mes });
  }

  private irA(queryParams: Record<string, string | null>): void {
    void this.router.navigate([], { queryParams, queryParamsHandling: 'merge' });
  }
}
