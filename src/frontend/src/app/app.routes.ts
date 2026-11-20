import { Routes } from '@angular/router';
import { RecursosPage } from './recursos/recursos.page';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'recursos' },
  { path: 'recursos', component: RecursosPage, title: 'Recursos · Reservas' },
  { path: '**', redirectTo: 'recursos' },
];
