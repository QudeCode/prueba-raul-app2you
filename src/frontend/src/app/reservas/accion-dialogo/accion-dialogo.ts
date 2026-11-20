import { Component, computed, input, output, signal } from '@angular/core';
import { Dialogo } from '../../common/dialogo/dialogo';
import { formatoDiaLargo } from '../../common/fechas';
import { nombreCompleto, Usuario } from '../../usuarios/usuario.model';
import { Reserva, textoHoras } from '../reserva.model';

export type AccionReserva = 'cancelar' | 'transferir';

/** Confirma cancelar una reserva, o elige a quién se transfiere. */
@Component({
  selector: 'app-accion-dialogo',
  imports: [Dialogo],
  templateUrl: './accion-dialogo.html',
  styleUrl: './accion-dialogo.scss',
})
export class AccionDialogo {
  readonly accion = input.required<AccionReserva>();
  readonly reserva = input.required<Reserva>();
  readonly usuarios = input.required<Usuario[]>();
  readonly enviando = input(false);
  readonly error = input<string | null>(null);

  readonly confirmar = output<number | null>();
  readonly cerrar = output();

  /** Candidatos a nuevo titular: todos menos el actual (regla 18). */
  protected readonly candidatos = computed(() =>
    this.usuarios().filter((u) => u.id !== this.reserva().titular.id),
  );

  private readonly elegido = signal<number | null>(null);
  protected readonly destino = computed(() => this.elegido() ?? this.candidatos()[0]?.id ?? null);

  protected readonly titulo: Record<AccionReserva, string> = {
    cancelar: 'Cancelar reserva',
    transferir: 'Transferir reserva',
  };
  protected readonly botonAceptar: Record<AccionReserva, string> = {
    cancelar: 'Cancelar reserva',
    transferir: 'Transferir',
  };
  protected readonly nombreCompleto = nombreCompleto;
  protected readonly formatoDiaLargo = formatoDiaLargo;
  protected readonly textoHoras = textoHoras;

  protected elegir(id: number): void {
    this.elegido.set(id);
  }

  protected aceptar(): void {
    this.confirmar.emit(this.accion() === 'transferir' ? this.destino() : null);
  }
}
