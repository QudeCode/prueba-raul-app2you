// Fechas como claves locales «YYYY-MM-DD» y meses «YYYY-MM», sin zona horaria: son las del contrato.
// Funciones puras, sin Angular.

export function dos(n: number): string {
  return String(n).padStart(2, '0');
}

export function claveDia(d: Date): string {
  return `${d.getFullYear()}-${dos(d.getMonth() + 1)}-${dos(d.getDate())}`;
}

export function deClaveDia(clave: string): Date {
  const [anio, mes, dia] = clave.split('-').map(Number);
  return new Date(anio, mes - 1, dia);
}

export function sumarDias(clave: string, n: number): string {
  const d = deClaveDia(clave);
  d.setDate(d.getDate() + n);
  return claveDia(d);
}

export function claveMes(clave: string): string {
  return clave.slice(0, 7);
}

export function sumarMeses(mes: string, n: number): string {
  const [anio, m] = mes.split('-').map(Number);
  return claveMes(claveDia(new Date(anio, m - 1 + n, 1)));
}

export function esClaveDia(valor: string | undefined): valor is string {
  return !!valor && /^\d{4}-\d{2}-\d{2}$/.test(valor) && claveDia(deClaveDia(valor)) === valor;
}

export function esClaveMes(valor: string | undefined): valor is string {
  return !!valor && /^\d{4}-\d{2}$/.test(valor) && esClaveDia(`${valor}-01`);
}

/** Semanas del mes, de lunes a domingo; `null` rellena los días de otros meses. */
export function semanasDelMes(mes: string): (string | null)[][] {
  const primero = deClaveDia(`${mes}-01`);
  const diasDelMes = new Date(primero.getFullYear(), primero.getMonth() + 1, 0).getDate();
  const huecos = (primero.getDay() + 6) % 7;
  const dias: (string | null)[] = Array(huecos).fill(null);
  for (let d = 1; d <= diasDelMes; d++) {
    dias.push(`${mes}-${dos(d)}`);
  }
  while (dias.length % 7 !== 0) {
    dias.push(null);
  }
  const semanas: (string | null)[][] = [];
  for (let i = 0; i < dias.length; i += 7) {
    semanas.push(dias.slice(i, i + 7));
  }
  return semanas;
}

/** «jueves, 3 de diciembre» (con año si `conAnio`). */
export function formatoDiaLargo(clave: string, conAnio = false): string {
  return new Intl.DateTimeFormat('es-ES', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    ...(conAnio ? { year: 'numeric' } : {}),
  }).format(deClaveDia(clave));
}

/** «diciembre de 2026». */
export function formatoMes(mes: string): string {
  return new Intl.DateTimeFormat('es-ES', { month: 'long', year: 'numeric' }).format(
    deClaveDia(`${mes}-01`),
  );
}
