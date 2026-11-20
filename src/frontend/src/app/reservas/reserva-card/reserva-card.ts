import { Component, input } from '@angular/core';
import { ESTADO_RESERVA_LABELS, POLITICA_CANCELACION_LABELS } from '../../common/enums';
import { claveMes, formatoDiaLargo } from '../../common/fechas';
import { RecursoCabecera } from '../../recursos/recurso-cabecera/recurso-cabecera';
import { nombreCompleto } from '../../usuarios/usuario.model';
import { Reserva, textoHoras } from '../reserva.model';

@Component({
  selector: 'app-reserva-card',
  imports: [RecursoCabecera],
  templateUrl: './reserva-card.html',
  styleUrl: './reserva-card.scss',
})
export class ReservaCard {
  readonly reserva = input.required<Reserva>();

  protected readonly estadoLabel = ESTADO_RESERVA_LABELS;
  protected readonly politicaLabel = POLITICA_CANCELACION_LABELS;
  protected readonly nombreCompleto = nombreCompleto;
  protected readonly textoHoras = textoHoras;
  protected readonly formatoDiaLargo = formatoDiaLargo;
  protected readonly claveMes = claveMes;
}
