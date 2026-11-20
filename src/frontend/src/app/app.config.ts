import { provideHttpClient, withFetch } from '@angular/common/http';
import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    // Los parámetros de la URL llegan como inputs de la página (decisión 0009)
    provideRouter(routes, withComponentInputBinding()),
    provideHttpClient(withFetch()),
  ],
};
