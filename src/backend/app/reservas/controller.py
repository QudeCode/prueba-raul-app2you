from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.reservas.dto import (
    DiaOcupadoRespuesta,
    DisponibilidadRespuesta,
    ReservaCreadaRespuesta,
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
# La URL cuelga del recurso, pero el código vive en reservas: recursos no depende de reservas (decisión 0015)
router_disponibilidad = APIRouter(
    prefix="/recursos/{recurso_id}/disponibilidad", tags=["disponibilidad"]
)

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


@router.get("/pendientes")
def pendientes(service: Reservas, usuario: UsuarioActual) -> list[ReservaRespuesta]:
    return service.pendientes(usuario)


# Después de /mias y /pendientes: FastAPI prueba las rutas en orden
@router.get("/{reserva_id}")
def obtener(service: Reservas, usuario: UsuarioActual, reserva_id: int) -> ReservaRespuesta:
    return service.obtener(reserva_id, usuario)


@router.post("", status_code=status.HTTP_201_CREATED)
def crear(
    service: Reservas, usuario: UsuarioActual, peticion: ReservaPeticion
) -> ReservaCreadaRespuesta:
    return service.crear(peticion, usuario)


@router.post("/{reserva_id}/aprobar")
def aprobar(service: Reservas, usuario: UsuarioActual, reserva_id: int) -> ReservaRespuesta:
    return service.aprobar(reserva_id, usuario)


@router.post("/{reserva_id}/rechazar")
def rechazar(service: Reservas, usuario: UsuarioActual, reserva_id: int) -> ReservaRespuesta:
    return service.rechazar(reserva_id, usuario)


@router.post("/{reserva_id}/cancelar")
def cancelar(service: Reservas, usuario: UsuarioActual, reserva_id: int) -> ReservaRespuesta:
    return service.cancelar(reserva_id, usuario)


@router.post("/{reserva_id}/transferir")
def transferir(
    service: Reservas, usuario: UsuarioActual, reserva_id: int, peticion: TransferenciaPeticion
) -> ReservaRespuesta:
    return service.transferir(reserva_id, peticion.nuevo_titular_id, usuario)
