from typing import Annotated

from fastapi import Depends

from app.common.enums import TipoRecurso
from app.recursos.dto import (
    EquipoRespuesta,
    RecursoRespuesta,
    SalaReunionRespuesta,
    VehiculoRespuesta,
)
from app.recursos.entity import Equipo, Recurso, SalaReunion, Vehiculo
from app.recursos.repository import RecursoRepository, get_recurso_repository


class RecursoService:
    def __init__(self, repositorio: RecursoRepository):
        self.repositorio = repositorio

    def listar(self, tipo: TipoRecurso | None = None) -> list[RecursoRespuesta]:
        return [self._a_respuesta(recurso) for recurso in self.repositorio.listar(tipo)]

    @staticmethod
    def _a_respuesta(recurso: Recurso) -> RecursoRespuesta:
        """Construye el DTO de su tipo; modalidad e imagen salen de las constantes de clase (decisión 0005)."""
        comunes = dict(
            id=recurso.id,
            nombre=recurso.nombre,
            descripcion=recurso.descripcion,
            politica_cancelacion=recurso.politica_cancelacion,
            modalidad_reserva=recurso.MODALIDAD_RESERVA,
            imagen=recurso.IMAGEN,
        )
        match recurso:
            case SalaReunion():
                return SalaReunionRespuesta(
                    **comunes,
                    capacidad_maxima=recurso.capacidad_maxima,
                    aforo_compartido=recurso.aforo_compartido,
                )
            case Vehiculo():
                return VehiculoRespuesta(
                    **comunes, matricula=recurso.matricula, plazas=recurso.plazas
                )
            case Equipo():
                return EquipoRespuesta(**comunes, numero_serie=recurso.numero_serie)
        raise TypeError(f"Tipo de recurso desconocido: {recurso.tipo}")


def get_recurso_service(
    repositorio: Annotated[RecursoRepository, Depends(get_recurso_repository)],
) -> RecursoService:
    return RecursoService(repositorio)
