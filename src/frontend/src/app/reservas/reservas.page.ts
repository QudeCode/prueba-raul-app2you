import { Component, computed, inject, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ahoraPorMinuto } from '../common/reloj';
import { claveDia } from '../common/fechas';
import { UsuariosService } from '../usuarios/usuarios.service';
import { ReservaCard } from './reserva-card/reserva-card';
import { Pestana, Reserva, pestanaDe } from './reserva.model';
import { ReservasService } from './reservas.service';

const PESTANAS: Pestana[] = ['activas', 'pasadas'];

const VACIO: Record<Pestana, string> = {
  activas: 'No tienes reservas activas.',
  pasadas: 'No hay reservas pasadas.',
};

@Component({
  selector: 'app-reservas-page',
  imports: [RouterLink, ReservaCard],
  templateUrl: './reservas.page.html',
  styleUrl: './reservas.page.scss',
})
export class ReservasPage {
  /** Parámetro `?pestana` de la URL (decisión 0009). */
  readonly pestana = input<string>();

  private readonly reservas = inject(ReservasService);
  protected readonly usuariosService = inject(UsuariosService);

  /** «Ahora» con precisión de minuto: las reservas cambian de pestaña a medianoche. */
  private readonly ahora = ahoraPorMinuto();

  /** La de la URL si existe; si no, `activas`. */
  protected readonly pestanaActiva = computed<Pestana>(
    () => PESTANAS.find((x) => x === this.pestana()) ?? 'activas',
  );

  protected readonly fuente = computed(() => this.reservas.mias);

  // value() lanza si el recurso está en error: solo se lee con hasValue()
  private readonly mias = computed(() =>
    this.reservas.mias.hasValue() ? this.reservas.mias.value() : [],
  );

  /** Activas en orden ascendente y pasadas en descendente. */
  private readonly porPestana = computed(() => {
    const hoy = claveDia(this.ahora());
    const activas: Reserva[] = [];
    const pasadas: Reserva[] = [];
    for (const r of this.mias()) {
      (pestanaDe(r, hoy) === 'activas' ? activas : pasadas).push(r);
    }
    return { activas, pasadas: pasadas.reverse() };
  });

  protected readonly visibles = computed<Reserva[]>(() => this.porPestana()[this.pestanaActiva()]);

  protected readonly cuentas = computed(() => ({
    activas: this.porPestana().activas.length,
    pasadas: this.porPestana().pasadas.length,
  }));

  protected readonly vacio = VACIO;
}
