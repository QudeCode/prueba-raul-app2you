import { httpResource } from '@angular/common/http';
import { computed, Injectable, signal } from '@angular/core';
import { API_URL } from '../common/api';
import { Usuario } from './usuario.model';

const CLAVE_USUARIO = 'reservas.usuarioId';

/** Usuarios y usuario actual (decisión 0011): la elección es de la sesión, no de una vista. */
@Injectable({ providedIn: 'root' })
export class UsuariosService {
  readonly usuarios = httpResource<Usuario[]>(() => `${API_URL}/usuarios`);

  private readonly elegidoId = signal<number | null>(this.leerGuardado());

  /** El elegido si sigue en la lista; si no, el primero; `null` mientras no hay lista. */
  readonly actual = computed<Usuario | null>(() => {
    const lista = this.usuarios.hasValue() ? this.usuarios.value() : [];
    return lista.find((u) => u.id === this.elegidoId()) ?? lista[0] ?? null;
  });

  readonly actualId = computed(() => this.actual()?.id ?? null);

  seleccionar(id: number): void {
    this.elegidoId.set(id);
    try {
      localStorage.setItem(CLAVE_USUARIO, String(id));
    } catch {
      // Sin almacenamiento disponible: la elección vale solo para esta sesión de la página
    }
  }

  private leerGuardado(): number | null {
    try {
      const id = Number(localStorage.getItem(CLAVE_USUARIO));
      return Number.isInteger(id) && id > 0 ? id : null;
    } catch {
      return null;
    }
  }
}
