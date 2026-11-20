import { httpResource } from '@angular/common/http';
import { Injectable, Signal } from '@angular/core';
import { API_URL } from '../common/api';
import { DiaOcupado, Disponibilidad } from './reserva.model';

/** Único conocedor de la API de reservas y disponibilidad (decisión 0008). */
@Injectable({ providedIn: 'root' })
export class ReservasService {
  disponibilidad(recursoId: Signal<number | null>, fecha: Signal<string | null>) {
    return httpResource<Disponibilidad>(() => {
      const id = recursoId();
      const dia = fecha();
      return id === null || dia === null
        ? undefined
        : { url: `${API_URL}/disponibilidad`, params: { recurso_id: id, fecha: dia } };
    });
  }

  mes(recursoId: Signal<number | null>, mes: Signal<string>) {
    return httpResource<DiaOcupado[]>(() => {
      const id = recursoId();
      if (id === null) {
        return undefined;
      }
      const [anio, numero] = mes().split('-').map(Number);
      return {
        url: `${API_URL}/disponibilidad/mes`,
        params: { recurso_id: id, anio, mes: numero },
      };
    });
  }
}
