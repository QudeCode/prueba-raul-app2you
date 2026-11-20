import { httpResource } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { API_URL } from '../common/api';
import { Recurso } from './recurso.model';

@Injectable({ providedIn: 'root' })
export class RecursosService {
  /**
   * Catálogo completo, pedido una vez y compartido; el filtro por tipo se aplica en memoria (decisión 0009).
   * La API también admite `?tipo=`, pero con «Todos» por defecto el listado ya tiene el catálogo entero.
   */
  readonly recursos = httpResource<Recurso[]>(() => `${API_URL}/recursos`);
}
