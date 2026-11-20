import { HttpResourceRef } from '@angular/common/http';
import { Component, computed, effect, input, output, signal, untracked } from '@angular/core';
import { Dialogo } from '../../common/dialogo/dialogo';
import { MODALIDAD_RESERVA_LABELS } from '../../common/enums';
import { formatoDiaLargo } from '../../common/fechas';
import { Recurso } from '../../recursos/recurso.model';
import { ReservasDelDia } from '../reservas-del-dia/reservas-del-dia';
import { Timeline } from '../timeline/timeline';
import {
  aHora,
  capacidadCompartida,
  ajustarSeleccion,
  aMinutos,
  diaReservable,
  Disponibilidad,
  disponibilidadPara,
  FIN_DIA,
  Modalidad,
  modalidadesDe,
  motivoNoReservable,
  pendientesQueEstorban,
  primerMinuto,
  ReservaNueva,
  Seleccion,
} from '../reserva.model';

/** Reservar un día de un recurso: elegir la modalidad y la franja, y ver quién ocupa el día. */
@Component({
  selector: 'app-reserva-modal',
  imports: [Dialogo, ReservasDelDia, Timeline],
  templateUrl: './reserva-modal.html',
  styleUrl: './reserva-modal.scss',
})
export class ReservaModal {
  readonly recurso = input.required<Recurso>();
  readonly fecha = input.required<string>();
  readonly ahora = input.required<Date>();
  readonly disponibilidad = input.required<HttpResourceRef<Disponibilidad | undefined>>();
  readonly enviando = input(false);
  readonly error = input<string | null>(null);
  /** A un responsable solo le bloquean las aprobadas (regla 8). */
  readonly responsable = input(false);

  readonly confirmar = output<ReservaNueva>();
  readonly cerrar = output();

  protected readonly desde = signal('');
  protected readonly hasta = signal('');
  protected readonly asistentes = signal<number | null>(1);
  private readonly eleccion = signal<Modalidad | null>(null);

  protected readonly modalidades = computed(() => modalidadesDe(this.recurso()));
  protected readonly modalidadLabel = MODALIDAD_RESERVA_LABELS;
  protected readonly titulo = computed(() => `Reservar · ${formatoDiaLargo(this.fecha(), true)}`);

  /** Fijada si el recurso solo admite una; en los demás, `null` hasta que se elige. */
  protected readonly modalidad = computed<Modalidad | null>(() => {
    const todas = this.modalidades();
    return todas.length === 1 ? todas[0] : this.eleccion();
  });

  protected readonly capacidad = computed(() => capacidadCompartida(this.recurso()));
  protected readonly aforo = computed(() => this.capacidad() !== null);
  protected readonly horaMaxima = aHora(FIN_DIA);

  /** Ninguna modalidad del recurso permite reservar este día: solo se consulta. */
  protected readonly soloConsulta = computed(
    () => !this.modalidades().some((m) => diaReservable(this.fecha(), m, this.ahora())),
  );

  /** La disponibilidad del día tal cual, con las pendientes. */
  protected readonly datos = computed(() => {
    const d = this.disponibilidad();
    return d.hasValue() ? d.value() : null;
  });

  /** Lo que el usuario actual puede reservar: sin las pendientes si es responsable. */
  protected readonly vista = computed(() => {
    const d = this.datos();
    return d && disponibilidadPara(d, this.responsable());
  });

  protected readonly seleccion = computed<Seleccion | null>(() =>
    this.desde() && this.hasta()
      ? { inicio: aMinutos(this.desde()), fin: aMinutos(this.hasta()) }
      : null,
  );

  protected readonly primerMinuto = computed(() => primerMinuto(this.fecha(), this.ahora()));

  protected readonly motivo = computed(() =>
    motivoNoReservable({
      recurso: this.recurso(),
      modalidad: this.modalidad() ?? (this.soloConsulta() ? this.modalidades()[0] : null),
      fecha: this.fecha(),
      seleccion: this.seleccion(),
      asistentes: this.asistentes(),
      disponibilidad: this.vista(),
      ahora: this.ahora(),
    }),
  );

  /** Pendientes que se rechazarán al confirmar (regla 8); solo para un responsable. */
  protected readonly estorban = computed(() => {
    const datos = this.datos();
    const modalidad = this.modalidad();
    if (!this.responsable() || this.motivo() !== null || !datos || !modalidad) {
      return [];
    }
    return pendientesQueEstorban({
      recurso: this.recurso(),
      modalidad,
      seleccion: this.seleccion(),
      asistentes: this.asistentes(),
      disponibilidad: datos,
    });
  });

  constructor() {
    // Al cambiar de día se borra la selección
    effect(() => {
      this.fecha();
      untracked(() => {
        this.desde.set('');
        this.hasta.set('');
      });
    });
  }

  protected elegirModalidad(modalidad: Modalidad): void {
    this.eleccion.set(modalidad);
  }

  protected elegirCelda(celda: Seleccion): void {
    const franjas = this.vista()?.franjas;
    if (!franjas) {
      return;
    }
    const nueva = ajustarSeleccion(
      this.seleccion(),
      celda,
      franjas,
      this.aforo() ? this.asistentes() : null,
      this.primerMinuto(),
    );
    if (nueva) {
      this.desde.set(aHora(nueva.inicio));
      this.hasta.set(aHora(nueva.fin));
    }
  }

  protected confirmarReserva(): void {
    const porHoras = this.modalidad() === 'POR_HORAS';
    this.confirmar.emit({
      recurso_id: this.recurso().id,
      fecha: this.fecha(),
      hora_inicio: porHoras ? this.desde() : null,
      hora_fin: porHoras ? this.hasta() : null,
      asistentes_sala: porHoras && this.aforo() ? this.asistentes() : null,
    });
  }

  protected leerAsistentes(campo: HTMLInputElement): void {
    this.asistentes.set(campo.value === '' ? null : campo.valueAsNumber);
  }
}
