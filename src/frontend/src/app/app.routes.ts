import { Routes } from '@angular/router';
import { RecursosPage } from './recursos/recursos.page';
import { ReservasPage } from './reservas/reservas.page';
import { RecursoDetallePage } from './reservas/recurso-detalle.page';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'recursos' },
  { path: 'recursos', component: RecursosPage, title: 'Recursos · Reservas' },
  { path: 'recursos/:id', component: RecursoDetallePage, title: 'Recurso · Reservas' },
  { path: 'reservas', component: ReservasPage, title: 'Reservas · Reservas' },
  { path: '**', redirectTo: 'recursos' },
];
