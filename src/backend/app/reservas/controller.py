from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.reservas.dto import DiaOcupadoRespuesta, DisponibilidadRespuesta
from app.reservas.service import DisponibilidadService, get_disponibilidad_service

router_disponibilidad = APIRouter(prefix="/disponibilidad", tags=["disponibilidad"])

Disponibilidad = Annotated[DisponibilidadService, Depends(get_disponibilidad_service)]


@router_disponibilidad.get("")
def consultar(service: Disponibilidad, recurso_id: int, fecha: date) -> DisponibilidadRespuesta:
    return service.consultar(recurso_id, fecha)


@router_disponibilidad.get("/mes")
def resumen_mes(
    service: Disponibilidad,
    recurso_id: int,
    anio: Annotated[int, Query(ge=2000, le=2100)],
    mes: Annotated[int, Query(ge=1, le=12)],
) -> list[DiaOcupadoRespuesta]:
    return service.resumen_mes(recurso_id, anio, mes)
