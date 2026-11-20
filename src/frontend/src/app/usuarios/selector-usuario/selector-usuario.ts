import { Component, computed, input, output } from '@angular/core';
import { ROL_LABELS } from '../../common/enums';
import { nombreCompleto, Usuario } from '../usuario.model';

@Component({
  selector: 'app-selector-usuario',
  templateUrl: './selector-usuario.html',
  styleUrl: './selector-usuario.scss',
})
export class SelectorUsuario {
  readonly usuarios = input.required<Usuario[]>();
  readonly actualId = input<number | null>(null);
  readonly cambiar = output<number>();

  /** Texto para lectores de pantalla: al cambiar de usuario se anuncia también su rol. */
  protected readonly anuncio = computed(() => {
    const u = this.usuarios().find((x) => x.id === this.actualId());
    return u ? `Usuario: ${nombreCompleto(u)} (${ROL_LABELS[u.rol]})` : '';
  });

  protected readonly rolLabel = ROL_LABELS;
  protected readonly nombreCompleto = nombreCompleto;
}
