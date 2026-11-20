import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { SelectorUsuario } from './usuarios/selector-usuario/selector-usuario';
import { UsuariosService } from './usuarios/usuarios.service';

@Component({
  imports: [RouterLink, RouterLinkActive, RouterOutlet, SelectorUsuario],
  selector: 'app-root',
  styleUrl: './app.scss',
  templateUrl: './app.html',
})
export class App {
  protected readonly usuariosService = inject(UsuariosService);

  /** Con el router, un `href="#…"` navegaría a `/#…` y perdería la URL actual: solo se mueve el foco. */
  protected saltarAlContenido(evento: Event): void {
    evento.preventDefault();
    document.getElementById('contenido')?.focus();
  }
}
