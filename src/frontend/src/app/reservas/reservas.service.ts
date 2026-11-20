import { HttpClient, httpResource } from '@angular/common/http';
import { inject, Injectable, Signal } from '@angular/core';
import { Observable, tap, throwError } from 'rxjs';
import { API_URL } from '../common/api';
import { esResponsable } from '../usuarios/usuario.model';
import { UsuariosService } from '../usuarios/usuarios.service';
import { DiaOcupado, Disponibilidad, Reserva, ReservaCreada, ReservaNueva } from './reserva.model';

/** Único conocedor de la API de reservas y disponibilidad (decisión 0008). */
@Injectable({ providedIn: 'root' })
export class ReservasService {
  private readonly http = inject(HttpClient);
  private readonly usuarios = inject(UsuariosService);

  /** Reservas del usuario actual. Leer su id hace que se pidan de nuevo al cambiar de usuario. */
  readonly mias = httpResource<Reserva[]>(() => {
    const headers = this.cabeceras();
    return headers ? { url: `${API_URL}/reservas/mias`, headers } : undefined;
  });

  /** Pendientes de aprobar: solo se piden si el usuario actual es responsable. */
  readonly pendientes = httpResource<Reserva[]>(() => {
    const headers = this.cabeceras();
    return headers && esResponsable(this.usuarios.actual())
      ? { url: `${API_URL}/reservas/pendientes`, headers }
      : undefined;
  });

  disponibilidad(recursoId: Signal<number | null>, fecha: Signal<string | null>) {
    return httpResource<Disponibilidad>(() => {
      const id = recursoId();
      const dia = fecha();
      return id === null || dia === null
        ? undefined
        : { url: `${API_URL}/recursos/${id}/disponibilidad`, params: { fecha: dia } };
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
        url: `${API_URL}/recursos/${id}/disponibilidad/mes`,
        params: { anio, mes: numero },
      };
    });
  }

  crear(nueva: ReservaNueva): Observable<ReservaCreada> {
    return this.accion<ReservaCreada>('', nueva);
  }

  aprobar(id: number): Observable<Reserva> {
    return this.accion(`/${id}/aprobar`);
  }

  rechazar(id: number): Observable<Reserva> {
    return this.accion(`/${id}/rechazar`);
  }

  cancelar(id: number): Observable<Reserva> {
    return this.accion(`/${id}/cancelar`);
  }

  transferir(id: number, nuevoTitularId: number): Observable<Reserva> {
    return this.accion(`/${id}/transferir`, { nuevo_titular_id: nuevoTitularId });
  }

  /** Cabecera del usuario actual (decisión 0011); `null` mientras no hay usuario. */
  private cabeceras(): Record<string, string> | null {
    const id = this.usuarios.actualId();
    return id === null ? null : { 'X-Usuario-Id': String(id) };
  }

  private accion<T extends Reserva = Reserva>(ruta: string, cuerpo?: object): Observable<T> {
    const headers = this.cabeceras();
    if (!headers) {
      return throwError(() => new Error('No hay usuario seleccionado.'));
    }
    return this.http.post<T>(`${API_URL}/reservas${ruta}`, cuerpo ?? null, { headers }).pipe(
      tap(() => {
        this.mias.reload();
        this.pendientes.reload();
      }),
    );
  }
}
