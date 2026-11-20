import { DestroyRef, inject, signal, Signal } from '@angular/core';

/** «Ahora» con precisión de minuto. Se llama desde un inicializador de campo (necesita el contexto de inyección). */
export function ahoraPorMinuto(): Signal<Date> {
  const ahora = signal(new Date());
  const temporizador = setInterval(() => ahora.set(new Date()), 60_000);
  inject(DestroyRef).onDestroy(() => clearInterval(temporizador));
  return ahora.asReadonly();
}
