// Réplica del contrato de GET /recursos (decisión 0008): mismos nombres de campo y unión por `tipo`.
// Lo usa también la funcionalidad de reservas; los enums y sus etiquetas están en common/enums.ts.
import { ModalidadReserva, PoliticaCancelacion } from '../common/enums';

interface RecursoComun {
  id: number;
  nombre: string;
  descripcion: string;
  politica_cancelacion: PoliticaCancelacion;
  modalidad_reserva: ModalidadReserva;
  imagen: string;
}

export interface SalaReunion extends RecursoComun {
  tipo: 'SALA_REUNION';
  capacidad_maxima: number;
  aforo_compartido: boolean;
}

export interface Vehiculo extends RecursoComun {
  tipo: 'VEHICULO';
  matricula: string;
  plazas: number;
}

export interface Equipo extends RecursoComun {
  tipo: 'EQUIPO';
  numero_serie: string;
}

export type Recurso = SalaReunion | Vehiculo | Equipo;
