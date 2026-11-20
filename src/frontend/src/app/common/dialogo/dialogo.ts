import { Component, effect, ElementRef, input, output, viewChild } from '@angular/core';

/** Envuelve un `<dialog>` nativo: `showModal()` atrapa el foco y Escape lo cierra (decisión 0010). */
@Component({
  selector: 'app-dialogo',
  templateUrl: './dialogo.html',
  styleUrl: './dialogo.scss',
})
export class Dialogo {
  readonly titulo = input.required<string>();
  readonly cerrar = output();

  private readonly dialogo = viewChild<ElementRef<HTMLDialogElement>>('dialogo');
  private pulsadoEnElFondo = false;

  constructor() {
    // showModal() solo funciona con el elemento ya en el DOM: se espera a que exista el viewChild.
    // El diálogo se abre al crearse; el padre lo quita del DOM al recibir `cerrar`.
    effect(() => {
      const elemento = this.dialogo()?.nativeElement;
      if (elemento && !elemento.open) {
        elemento.showModal();
      }
    });
  }

  /** Evento `close`: también se dispara con Escape, y el padre actualiza su estado. */
  protected alCerrar(): void {
    this.cerrar.emit();
  }

  protected alPulsar(evento: MouseEvent, elemento: HTMLDialogElement): void {
    this.pulsadoEnElFondo = evento.target === elemento;
  }

  /** Cierra solo si el botón se pulsó y se soltó en el fondo: arrastrar una selección de texto no lo cierra. */
  protected alClicar(evento: MouseEvent, elemento: HTMLDialogElement): void {
    if (this.pulsadoEnElFondo && evento.target === elemento) {
      elemento.close();
    }
    this.pulsadoEnElFondo = false;
  }
}
