import { HttpResourceRef } from '@angular/common/http';
import {
  Component,
  computed,
  effect,
  input,
  linkedSignal,
  output,
  signal,
  untracked,
} from '@angular/core';
import { Dialogo } from '../../common/dialogo/dialogo';
import { MODALIDAD_RESERVA_LABELS } from '../../common/enums';
import { formatoDiaLargo, formatoRango } from '../../common/fechas';
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
  plazasLibres,
  primerMinuto,
  ReservaNueva,
  Seleccion,
  ultimosDiasPosibles,
} from '../reserva.model';

/** Reservar un recurso: elegir la modalidad y la franja o los días, y ver quién los ocupa. */
@Component({
  selector: 'app-reserva-modal',
  imports: [Dialogo, ReservasDelDia, Timeline],
  templateUrl: './reserva-modal.html',
  styleUrl: './reserva-modal.scss',
})
export class ReservaModal {
  readonly recurso = input.required<Recurso>();
  readonly fecha = input.required<string>();
  /** Último día de una reserva de día completo de varios días; `null` si es de uno (regla 1). */
  readonly fechaFin = input<string | null>(null);
  readonly ahora = input.required<Date>();
  readonly disponibilidad = input.required<HttpResourceRef<Disponibilidad | undefined>>();
  readonly enviando = input(false);
  readonly error = input<string | null>(null);
  /** A un responsable solo le bloquean las aprobadas (regla 8). */
  readonly responsable = input(false);

  readonly confirmar = output<ReservaNueva>();
  readonly cambiarFechaFin = output<string | null>();
  readonly cerrar = output();

  protected readonly desde = signal('');
  protected readonly hasta = signal('');
  protected readonly asistentes = signal<number | null>(1);
  private readonly eleccion = signal<Modalidad | null>(null);

  protected readonly modalidades = computed(() => modalidadesDe(this.recurso()));
  protected readonly modalidadLabel = MODALIDAD_RESERVA_LABELS;
  protected readonly ultimoDia = computed(() => this.fechaFin() ?? this.fecha());
  protected readonly titulo = computed(
    () => `Reservar · ${formatoRango(this.fecha(), this.ultimoDia(), true)}`,
  );

  /** Los días que se pueden elegir como último, con cuántos días abarcaría la reserva. */
  protected readonly ultimosDias = computed(() =>
    ultimosDiasPosibles(this.fecha()).map((clave, i) => ({
      clave,
      texto: i === 0 ? formatoDiaLargo(clave) : `${formatoDiaLargo(clave)} (${i + 1} días)`,
    })),
  );

  /**
   * Fijada si el recurso solo admite una; en los demás, `null` hasta que se elige. Con varios días
   * en la URL, es día completo.
   */
  protected readonly modalidad = computed<Modalidad | null>(() => {
    const todas = this.modalidades();
    if (todas.length === 1) {
      return todas[0];
    }
    return this.eleccion() ?? (this.fechaFin() ? 'DIA_COMPLETO' : null);
  });

  protected readonly capacidad = computed(() => capacidadCompartida(this.recurso()));
  protected readonly aforo = computed(() => this.capacidad() !== null);
  protected readonly horaMaxima = aHora(FIN_DIA);

  /** Ninguna modalidad del recurso permite reservar este día: solo se consulta. */
  protected readonly soloConsulta = computed(
    () => !this.modalidades().some((m) => diaReservable(this.fecha(), m, this.ahora())),
  );

  protected readonly cargando = computed(() => this.disponibilidad().isLoading());

  /**
   * La disponibilidad tal cual, con las pendientes. Mientras se recarga (otro último día) se
   * conserva la anterior, para que el modal no se vacíe ni el selector pierda el foco.
   */
  protected readonly datos = linkedSignal({
    source: () => {
      const d = this.disponibilidad();
      return { valor: d.hasValue() ? d.value() : null, cargando: d.isLoading() };
    },
    computation: ({ valor, cargando }, previo?: { value: Disponibilidad | null }) =>
      valor ?? (cargando ? (previo?.value ?? null) : null),
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

  /** Con aforo, cuántas personas caben aún en la franja elegida, según lo que puede reservar el usuario. */
  protected readonly plazas = computed(() =>
    this.aforo() ? plazasLibres(this.vista()?.franjas ?? null, this.seleccion()) : null,
  );

  protected readonly motivo = computed(() =>
    motivoNoReservable({
      recurso: this.recurso(),
      modalidad: this.modalidad() ?? (this.soloConsulta() ? this.modalidades()[0] : null),
      fecha: this.fecha(),
      fechaFin: this.fechaFin(),
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
    // Por horas es un solo día: la disponibilidad vuelve a ser la del día, con sus franjas. También
    // si se vuelve atrás en el navegador a una URL con varios días y la modalidad por horas
    effect(() => {
      if (this.modalidad() === 'POR_HORAS' && this.fechaFin() !== null) {
        untracked(() => this.cambiarFechaFin.emit(null));
      }
    });
  }

  protected elegirModalidad(modalidad: Modalidad): void {
    this.eleccion.set(modalidad);
  }

  protected elegirUltimoDia(clave: string): void {
    this.cambiarFechaFin.emit(clave === this.fecha() ? null : clave);
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
      fecha_fin: porHoras ? null : this.fechaFin(),
      hora_inicio: porHoras ? this.desde() : null,
      hora_fin: porHoras ? this.hasta() : null,
      asistentes_sala: porHoras && this.aforo() ? this.asistentes() : null,
    });
  }

  protected leerAsistentes(campo: HTMLInputElement): void {
    this.asistentes.set(campo.value === '' ? null : campo.valueAsNumber);
  }
}
