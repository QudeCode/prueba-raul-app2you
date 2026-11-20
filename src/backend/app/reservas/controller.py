from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.reservas.dto import (
    DiaOcupadoRespuesta,
    DisponibilidadRespuesta,
    ReservaPeticion,
    ReservaRespuesta,
    TransferenciaPeticion,
)
from app.reservas.service import (
    DisponibilidadService,
    ReservaService,
    get_disponibilidad_service,
    get_reserva_service,
)
from app.usuarios.controller import UsuarioActual

router = APIRouter(prefix="/reservas", tags=["reservas"])
router_disponibilidad = APIRouter(prefix="/disponibilidad", tags=["disponibilidad"])

Reservas = Annotated[ReservaService, Depends(get_reserva_service)]
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


@router.get("/mias")
def mias(service: Reservas, usuario: UsuarioActual) -> list[ReservaRespuesta]:
    return service.mias(usuario)


@router.post("", status_code=status.HTTP_201_CREATED)
def crear(service: Reservas, usuario: UsuarioActual, peticion: ReservaPeticion) -> ReservaRespuesta:
    return service.crear(peticion, usuario)


@router.post("/{reserva_id}/cancelar")
def cancelar(service: Reservas, usuario: UsuarioActual, reserva_id: int) -> ReservaRespuesta:
    return service.cancelar(reserva_id, usuario)


@router.post("/{reserva_id}/transferir")
def transferir(
    service: Reservas, usuario: UsuarioActual, reserva_id: int, peticion: TransferenciaPeticion
) -> ReservaRespuesta:
    return service.transferir(reserva_id, peticion.nuevo_titular_id, usuario)
