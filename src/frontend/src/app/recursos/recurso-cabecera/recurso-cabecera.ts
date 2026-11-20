import { Component, input } from '@angular/core';
import { Params, RouterLink } from '@angular/router';
import { TIPO_RECURSO_LABELS } from '../../common/enums';
import { Recurso } from '../recurso.model';

/** Imagen, nombre y tipo de un recurso, compartidos por la tarjeta del catálogo y la de reserva. */
@Component({
  selector: 'app-recurso-cabecera',
  imports: [RouterLink],
  templateUrl: './recurso-cabecera.html',
  styleUrl: './recurso-cabecera.scss',
})
export class RecursoCabecera {
  readonly recurso = input.required<Recurso>();
  /** Si lo hay, el nombre es un enlace que cubre toda la tarjeta (con `::after`). */
  readonly enlace = input<string | null>(null);
  readonly parametros = input<Params | null>(null);

  protected readonly tipoLabel = TIPO_RECURSO_LABELS;
}
