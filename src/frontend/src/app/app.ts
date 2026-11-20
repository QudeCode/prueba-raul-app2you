import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';

const API = 'http://localhost:8000';

// Comprobación provisional de que el frontend llega a cada GET del backend
const RUTAS = ['/usuarios', '/recursos'];

@Component({
  imports: [RouterOutlet],
  selector: 'app-root',
  styleUrl: './app.scss',
  templateUrl: './app.html',
})
export class App {
  protected readonly respuestas = signal<{ ruta: string; resultado: string }[]>([]);

  constructor() {
    Promise.all(
      RUTAS.map(async (ruta) => {
        try {
          const respuesta = await fetch(API + ruta);
          return { ruta, resultado: `${respuesta.status} ${await respuesta.text()}` };
        } catch {
          return { ruta, resultado: 'sin conexión con el backend' };
        }
      }),
    ).then((respuestas) => this.respuestas.set(respuestas));
  }
}
