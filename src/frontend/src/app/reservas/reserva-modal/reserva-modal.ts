import { HttpResourceRef } from '@angular/common/http';
import { Component, computed, input, output } from '@angular/core';
import { Dialogo } from '../../common/dialogo/dialogo';
import { formatoDiaLargo } from '../../common/fechas';
import { Recurso } from '../../recursos/recurso.model';
import { ReservasDelDia } from '../reservas-del-dia/reservas-del-dia';
import {
  diaReservable,
  Disponibilidad,
  modalidadesDe,
  motivoNoReservable,
  ReservaNueva,
} from '../reserva.model';

/** Reservar un día completo de un recurso, y ver quién ocupa el día. */
@Component({
  selector: 'app-reserva-modal',
  imports: [Dialogo, ReservasDelDia],
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

  readonly confirmar = output<ReservaNueva>();
  readonly cerrar = output();

  protected readonly titulo = computed(() => `Reservar · ${formatoDiaLargo(this.fecha(), true)}`);

  /** Sin día completo, o con el día ya no reservable, solo se consulta. */
  protected readonly soloConsulta = computed(
    () =>
      !modalidadesDe(this.recurso()).includes('DIA_COMPLETO') ||
      !diaReservable(this.fecha(), 'DIA_COMPLETO', this.ahora()),
  );

  protected readonly datos = computed(() => {
    const d = this.disponibilidad();
    return d.hasValue() ? d.value() : null;
  });

  protected readonly motivo = computed(() =>
    motivoNoReservable({
      recurso: this.recurso(),
      modalidad: 'DIA_COMPLETO',
      fecha: this.fecha(),
      seleccion: null,
      asistentes: null,
      disponibilidad: this.datos(),
      ahora: this.ahora(),
    }),
  );

  protected confirmarReserva(): void {
    this.confirmar.emit({
      recurso_id: this.recurso().id,
      fecha: this.fecha(),
      hora_inicio: null,
      hora_fin: null,
      asistentes_sala: null,
    });
  }
}
