import {
  Component,
  computed,
  effect,
  ElementRef,
  inject,
  input,
  signal,
  untracked,
  viewChild,
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { Observable } from 'rxjs';
import { mensajeDeError } from '../common/api';
import { ahoraPorMinuto } from '../common/reloj';
import { claveDia } from '../common/fechas';
import { UsuariosService } from '../usuarios/usuarios.service';
import { AccionDialogo, AccionReserva } from './accion-dialogo/accion-dialogo';
import { AccionesReserva, ReservaCard } from './reserva-card/reserva-card';
import { Pestana, Reserva, pestanaDe } from './reserva.model';
import { ReservasService } from './reservas.service';

const PESTANAS: Pestana[] = ['activas', 'pasadas'];

const VACIO: Record<Pestana, string> = {
  activas: 'No tienes reservas activas.',
  pasadas: 'No hay reservas pasadas.',
};

@Component({
  selector: 'app-reservas-page',
  imports: [RouterLink, ReservaCard, AccionDialogo],
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
  private readonly titulo = viewChild<ElementRef<HTMLElement>>('titulo');

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

  constructor() {
    // El resultado de una acción no se arrastra a otra pestaña ni a otro usuario
    effect(() => {
      this.pestanaActiva();
      this.usuariosService.actualId();
      untracked(() => this.mensaje.set(null));
    });
  }

  protected readonly accionando = signal(false);
  protected readonly mensaje = signal<string | null>(null);
  protected readonly error = signal<string | null>(null);
  protected readonly dialogo = signal<{
    accion: AccionReserva;
    reserva: Reserva;
  } | null>(null);

  /** Acciones de cada tarjeta según lo que calcula el backend (plazos de las reglas 14 a 19). */
  protected accionesDe(reserva: Reserva): AccionesReserva {
    const activa = this.pestanaActiva() === 'activas';
    return {
      cancelar: activa && reserva.puede_cancelar,
      transferir: activa && reserva.puede_transferir,
    };
  }

  protected abrirDialogo(accion: AccionReserva, reserva: Reserva): void {
    this.mensaje.set(null);
    this.error.set(null);
    this.dialogo.set({ accion, reserva });
  }

  protected cerrarDialogo(): void {
    this.dialogo.set(null);
    this.error.set(null);
  }

  protected confirmarDialogo(nuevoTitularId: number | null): void {
    const abierto = this.dialogo();
    if (!abierto) {
      return;
    }
    if (abierto.accion === 'cancelar') {
      this.ejecutar(this.reservas.cancelar(abierto.reserva.id), 'Reserva cancelada.');
    } else if (nuevoTitularId !== null) {
      this.ejecutar(
        this.reservas.transferir(abierto.reserva.id, nuevoTitularId),
        'Reserva transferida.',
      );
    }
  }

  private ejecutar(peticion: Observable<Reserva>, exito: string): void {
    this.accionando.set(true);
    this.mensaje.set(null);
    this.error.set(null);
    peticion.subscribe({
      next: () => {
        this.accionando.set(false);
        this.mensaje.set(exito);
        this.dialogo.set(null);
        // El diálogo desaparece en la siguiente detección de cambios: el foco se mueve después
        setTimeout(() => this.titulo()?.nativeElement.focus());
      },
      error: (error: unknown) => {
        this.accionando.set(false);
        this.error.set(mensajeDeError(error));
      },
    });
  }
}
