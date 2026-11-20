from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import ModalidadReserva, PoliticaCancelacion, TipoRecurso


class RecursoComun(BaseModel):
    """Campos que comparten todas las respuestas de recurso; no se expone sola."""

    # Sin esto, el valor por defecto de `tipo` lo dejaría como opcional en el esquema de respuesta
    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    id: int
    nombre: str
    descripcion: str
    politica_cancelacion: PoliticaCancelacion
    modalidad_reserva: ModalidadReserva
    imagen: str


class SalaReunionRespuesta(RecursoComun):
    tipo: Literal[TipoRecurso.SALA_REUNION] = TipoRecurso.SALA_REUNION
    capacidad_maxima: int
    aforo_compartido: bool


class VehiculoRespuesta(RecursoComun):
    tipo: Literal[TipoRecurso.VEHICULO] = TipoRecurso.VEHICULO
    matricula: str
    plazas: int


class EquipoRespuesta(RecursoComun):
    tipo: Literal[TipoRecurso.EQUIPO] = TipoRecurso.EQUIPO
    numero_serie: str


RecursoRespuesta = Annotated[
    SalaReunionRespuesta | VehiculoRespuesta | EquipoRespuesta, Field(discriminator="tipo")
]
