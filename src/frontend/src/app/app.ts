import { Component } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';

@Component({
  imports: [RouterLink, RouterOutlet],
  selector: 'app-root',
  styleUrl: './app.scss',
  templateUrl: './app.html',
})
export class App {
  /** Con el router, un `href="#…"` navegaría a `/#…` y perdería la URL actual: solo se mueve el foco. */
  protected saltarAlContenido(evento: Event): void {
    evento.preventDefault();
    document.getElementById('contenido')?.focus();
  }
}
