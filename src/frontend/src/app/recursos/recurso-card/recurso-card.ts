import { Component, input } from '@angular/core';
import {
  MODALIDAD_RESERVA_LABELS,
  POLITICA_CANCELACION_LABELS,
  TIPO_RECURSO_LABELS,
} from '../../common/enums';
import { Recurso } from '../recurso.model';

@Component({
  selector: 'app-recurso-card',
  templateUrl: './recurso-card.html',
  styleUrl: './recurso-card.scss',
})
export class RecursoCard {
  readonly recurso = input.required<Recurso>();

  protected readonly tipoLabel = TIPO_RECURSO_LABELS;
  protected readonly politicaLabel = POLITICA_CANCELACION_LABELS;
  protected readonly modalidadLabel = MODALIDAD_RESERVA_LABELS;
}
