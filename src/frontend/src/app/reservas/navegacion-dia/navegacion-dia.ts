import { Component, input, output, signal } from '@angular/core';
import { formatoDiaLargo, sumarDias } from '../../common/fechas';
import { Calendario } from '../calendario/calendario';

/** «Día anterior» y «Día siguiente», y la fecha, que despliega un calendario compacto. */
@Component({
  selector: 'app-navegacion-dia',
  imports: [Calendario],
  templateUrl: './navegacion-dia.html',
  styleUrl: './navegacion-dia.scss',
})
export class NavegacionDia {
  readonly fecha = input.required<string>();
  readonly primerDiaElegible = input.required<string>();
  readonly mes = input.required<string>();
  readonly conteos = input<Record<string, number>>({});
  readonly marcarLibre = input(false);

  readonly cambiarFecha = output<string>();
  readonly cambiarMes = output<string>();

  protected readonly desplegado = signal(false);

  protected readonly formatoDiaLargo = formatoDiaLargo;
  protected readonly sumarDias = sumarDias;

  protected elegir(dia: string): void {
    this.desplegado.set(false);
    this.cambiarFecha.emit(dia);
  }

  /** Escape cierra el desplegable sin llegar al diálogo, que cerraría el modal entero. */
  protected cerrarConEscape(evento: Event): void {
    if (this.desplegado()) {
      evento.preventDefault();
      evento.stopPropagation();
      this.desplegado.set(false);
    }
  }
}
