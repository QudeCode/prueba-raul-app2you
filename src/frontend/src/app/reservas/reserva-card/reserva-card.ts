import { Component, input, output } from '@angular/core';
import { ESTADO_RESERVA_LABELS, POLITICA_CANCELACION_LABELS } from '../../common/enums';
import { claveMes, formatoDiaLargo } from '../../common/fechas';
import { RecursoCabecera } from '../../recursos/recurso-cabecera/recurso-cabecera';
import { nombreCompleto } from '../../usuarios/usuario.model';
import { Reserva, textoHoras } from '../reserva.model';

export interface AccionesReserva {
  cancelar: boolean;
  transferir: boolean;
  aprobar: boolean;
  rechazar: boolean;
}

@Component({
  selector: 'app-reserva-card',
  imports: [RecursoCabecera],
  templateUrl: './reserva-card.html',
  styleUrl: './reserva-card.scss',
})
export class ReservaCard {
  readonly reserva = input.required<Reserva>();
  readonly mostrarTitular = input(false);
  readonly acciones = input<AccionesReserva>({
    cancelar: false,
    transferir: false,
    aprobar: false,
    rechazar: false,
  });
  /** Deshabilita los botones mientras hay una acción en curso. */
  readonly ocupada = input(false);

  readonly cancelar = output();
  readonly transferir = output();
  readonly aprobar = output();
  readonly rechazar = output();

  protected readonly estadoLabel = ESTADO_RESERVA_LABELS;
  protected readonly politicaLabel = POLITICA_CANCELACION_LABELS;
  protected readonly nombreCompleto = nombreCompleto;
  protected readonly textoHoras = textoHoras;
  protected readonly formatoDiaLargo = formatoDiaLargo;
  protected readonly claveMes = claveMes;

  /** «Cancelar reserva de Sala Mar el jueves, 3 de diciembre de 2026»: el contexto de cada botón. */
  protected contexto(verbo: string): string {
    const r = this.reserva();
    return `${verbo} reserva de ${r.recurso.nombre} el ${formatoDiaLargo(r.fecha, true)}`;
  }

  protected hayAcciones(): boolean {
    return Object.values(this.acciones()).some(Boolean);
  }
}
