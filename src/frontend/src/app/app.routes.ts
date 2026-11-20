import { Routes } from '@angular/router';
import { RecursosPage } from './recursos/recursos.page';
import { RecursoDetallePage } from './reservas/recurso-detalle.page';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'recursos' },
  { path: 'recursos', component: RecursosPage, title: 'Recursos · Reservas' },
  { path: 'recursos/:id', component: RecursoDetallePage, title: 'Recurso · Reservas' },
  { path: '**', redirectTo: 'recursos' },
];
