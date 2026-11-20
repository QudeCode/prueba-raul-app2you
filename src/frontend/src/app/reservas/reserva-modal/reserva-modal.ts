import { HttpResourceRef } from '@angular/common/http';
import { Component, computed, input, output } from '@angular/core';
import { Dialogo } from '../../common/dialogo/dialogo';
import { formatoDiaLargo } from '../../common/fechas';
import { ReservasDelDia } from '../reservas-del-dia/reservas-del-dia';
import { Disponibilidad } from '../reserva.model';

/** Consultar un día de un recurso: quién lo ocupa. */
@Component({
  selector: 'app-reserva-modal',
  imports: [Dialogo, ReservasDelDia],
  templateUrl: './reserva-modal.html',
  styleUrl: './reserva-modal.scss',
})
export class ReservaModal {
  readonly fecha = input.required<string>();
  readonly disponibilidad = input.required<HttpResourceRef<Disponibilidad | undefined>>();

  readonly cerrar = output();

  protected readonly titulo = computed(() => formatoDiaLargo(this.fecha(), true));

  protected readonly datos = computed(() => {
    const d = this.disponibilidad();
    return d.hasValue() ? d.value() : null;
  });
}
