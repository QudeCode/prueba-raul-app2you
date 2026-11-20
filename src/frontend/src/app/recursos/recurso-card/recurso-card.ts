import { Component, input } from '@angular/core';
import { MODALIDAD_RESERVA_LABELS, POLITICA_CANCELACION_LABELS } from '../../common/enums';
import { RecursoCabecera } from '../recurso-cabecera/recurso-cabecera';
import { Recurso } from '../recurso.model';

@Component({
  imports: [RecursoCabecera],
  selector: 'app-recurso-card',
  templateUrl: './recurso-card.html',
  styleUrl: './recurso-card.scss',
})
export class RecursoCard {
  readonly recurso = input.required<Recurso>();
  /** Con `true`, el nombre enlaza al detalle. El detalle la usa con `false`: el clic no debe cambiar la URL. */
  readonly enlazar = input(true);

  protected readonly politicaLabel = POLITICA_CANCELACION_LABELS;
  protected readonly modalidadLabel = MODALIDAD_RESERVA_LABELS;
}
