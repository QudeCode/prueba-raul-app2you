import { Component, input } from '@angular/core';
import { ESTADO_RESERVA_LABELS } from '../../common/enums';
import { nombreCompleto } from '../../usuarios/usuario.model';
import { Reserva, textoOcupacion } from '../reserva.model';

/** Lista accesible de las reservas activas de un día o un rango: explica por qué no está libre (regla 20). */
@Component({
  selector: 'app-reservas-del-dia',
  templateUrl: './reservas-del-dia.html',
  styleUrl: './reservas-del-dia.scss',
})
export class ReservasDelDia {
  readonly reservas = input.required<Reserva[]>();
  /** Las reservas pueden ser de días distintos: cada una dice el suyo. */
  readonly conDia = input(false);

  protected readonly estadoLabel = ESTADO_RESERVA_LABELS;
  protected readonly nombreCompleto = nombreCompleto;
  protected readonly textoOcupacion = textoOcupacion;
}
