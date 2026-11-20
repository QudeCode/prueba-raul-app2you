import { Component, computed, effect, inject, input, signal, untracked } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { mensajeDeError } from '../common/api';
import { ahoraPorMinuto } from '../common/reloj';
import { claveDia, claveMes, esClaveDia, esClaveMes } from '../common/fechas';
import { RecursoCard } from '../recursos/recurso-card/recurso-card';
import { RecursosService } from '../recursos/recursos.service';
import { esResponsable } from '../usuarios/usuario.model';
import { UsuariosService } from '../usuarios/usuarios.service';
import { Calendario } from './calendario/calendario';
import { NavegacionDia } from './navegacion-dia/navegacion-dia';
import {
  modalidadesDe,
  primerDiaElegible,
  Reserva,
  ReservaCreada,
  ReservaNueva,
  soloDiaCompleto,
  textoRechazadas,
  ultimosDiasPosibles,
} from './reserva.model';
import { ReservaModal } from './reserva-modal/reserva-modal';
import { ReservasDelDia } from './reservas-del-dia/reservas-del-dia';
import { ReservasService } from './reservas.service';

@Component({
  selector: 'app-recurso-detalle-page',
  imports: [RouterLink, RecursoCard, Calendario, NavegacionDia, ReservaModal, ReservasDelDia],
  templateUrl: './recurso-detalle.page.html',
  styleUrl: './recurso-detalle.page.scss',
})
export class RecursoDetallePage {
  /** Parámetros de la URL (decisión 0009): `/recursos/:id?mes=YYYY-MM&fecha=YYYY-MM-DD&hasta=YYYY-MM-DD`. */
  readonly id = input<string>();
  readonly mes = input<string>();
  readonly fecha = input<string>();
  readonly hasta = input<string>();

  private readonly router = inject(Router);
  private readonly reservas = inject(ReservasService);
  protected readonly recursos = inject(RecursosService).recursos;
  private readonly usuarios = inject(UsuariosService);

  /** A un responsable solo le bloquean las aprobadas (regla 8). */
  protected readonly responsable = computed(() => esResponsable(this.usuarios.actual()));

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

  /** Con `fecha` válida, el modal está abierto en ese día. */
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

  /**
   * Último día de una reserva de día completo de varios días (regla 1); `null` si es de uno o el
   * recurso no se reserva por días completos.
   */
  protected readonly hastaActiva = computed(() => {
    const fecha = this.fechaActiva();
    const hasta = this.hasta();
    const recurso = this.recurso();
    const porDias = recurso !== undefined && modalidadesDe(recurso).includes('DIA_COMPLETO');
    return porDias &&
      fecha &&
      hasta &&
      hasta !== fecha &&
      ultimosDiasPosibles(fecha).includes(hasta)
      ? hasta
      : null;
  });

  private readonly recursoId = computed(() => this.recurso()?.id ?? null);

  protected readonly mesReservas = this.reservas.mes(this.recursoId, this.mesActivo);
  protected readonly disponibilidad = this.reservas.disponibilidad(
    this.recursoId,
    this.fechaActiva,
    this.hastaActiva,
  );

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

  protected readonly enviando = signal(false);
  protected readonly errorReserva = signal<string | null>(null);
  protected readonly aviso = signal<string | null>(null);
  /** Pendientes que acaba de rechazar el responsable al reservar (regla 8). */
  protected readonly rechazadas = signal<Reserva[]>([]);
  protected readonly textoRechazadas = textoRechazadas;

  constructor() {
    // El error de la API es de los días en los que se produjo
    effect(() => {
      this.fechaActiva();
      this.hastaActiva();
      untracked(() => this.errorReserva.set(null));
    });
  }

  protected elegirDia(fecha: string): void {
    this.aviso.set(null);
    this.rechazadas.set([]);
    this.irA({ fecha, mes: claveMes(fecha), hasta: null });
  }

  protected cambiarHasta(hasta: string | null): void {
    this.irA({ hasta });
  }

  protected cambiarMes(mes: string): void {
    this.irA({ mes });
  }

  protected cerrarModal(): void {
    this.irA({ fecha: null, hasta: null });
  }

  protected reservar(nueva: ReservaNueva): void {
    this.enviando.set(true);
    this.errorReserva.set(null);
    this.reservas.crear(nueva).subscribe({
      next: (reserva: ReservaCreada) => {
        this.enviando.set(false);
        this.aviso.set(
          reserva.estado === 'APROBADA'
            ? 'Reserva creada y aprobada.'
            : 'Reserva creada: pendiente de aprobación.',
        );
        this.rechazadas.set(reserva.rechazadas);
        this.cerrarModal();
        this.mesReservas.reload();
        this.disponibilidad.reload();
      },
      error: (error: unknown) => {
        this.enviando.set(false);
        this.errorReserva.set(mensajeDeError(error));
        // El día ha podido cambiar desde que se abrió el modal
        this.disponibilidad.reload();
      },
    });
  }

  private irA(queryParams: Record<string, string | null>): void {
    void this.router.navigate([], { queryParams, queryParamsHandling: 'merge' });
  }
}
