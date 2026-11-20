import { Component, computed, inject, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { esTipoRecurso, TIPO_RECURSO_PLURAL, TIPOS_RECURSO, TipoRecurso } from '../common/enums';
import { RecursoCard } from './recurso-card/recurso-card';
import { RecursosService } from './recursos.service';

@Component({
  selector: 'app-recursos-page',
  imports: [RouterLink, RecursoCard],
  templateUrl: './recursos.page.html',
  styleUrl: './recursos.page.scss',
})
export class RecursosPage {
  /** Parámetro `?tipo` de la URL (decisión 0009). */
  readonly tipo = input<string>();

  /** Un tipo desconocido en la URL se trata como «todos». */
  protected readonly tipoActivo = computed(() => {
    const tipo = this.tipo();
    return esTipoRecurso(tipo) ? tipo : null;
  });

  protected readonly recursos = inject(RecursosService).recursos;

  // value() lanza si el recurso está en error: el catálogo solo se lee con hasValue()
  private readonly catalogo = computed(() =>
    this.recursos.hasValue() ? this.recursos.value() : [],
  );

  /** Filtro por tipo en memoria sobre el catálogo completo (decisión 0009). */
  protected readonly visibles = computed(() => {
    const tipo = this.tipoActivo();
    return tipo ? this.catalogo().filter((r) => r.tipo === tipo) : this.catalogo();
  });

  protected readonly catalogoTotal = computed(() => this.catalogo().length);

  /** Recursos de cada tipo, sobre el catálogo completo, para el filtro. */
  protected readonly conteos = computed(() => {
    const conteos = Object.fromEntries(TIPOS_RECURSO.map((t) => [t, 0])) as Record<
      TipoRecurso,
      number
    >;
    for (const r of this.catalogo()) {
      conteos[r.tipo]++;
    }
    return conteos;
  });

  protected readonly tipos = TIPOS_RECURSO;
  protected readonly plural = TIPO_RECURSO_PLURAL;
}
