from datetime import date
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload

from app.common.enums import EstadoReserva
from app.database import get_session
from app.reservas.entity import Reserva

# Solo las activas ocupan el recurso (reglas de negocio, «Reserva activa»)
ESTADOS_ACTIVOS = (EstadoReserva.PENDIENTE, EstadoReserva.APROBADA)

# Por fecha y hora; los días completos (sin hora) primero
ORDEN = (Reserva.fecha, Reserva.hora_inicio.asc().nulls_first(), Reserva.id)


def _con_relaciones(consulta: Select[tuple[Reserva]]) -> Select[tuple[Reserva]]:
    return consulta.options(
        joinedload(Reserva.recurso), joinedload(Reserva.titular), joinedload(Reserva.aprobada_por)
    )


class ReservaRepository:
    def __init__(self, session: Session):
        self.session = session

    def activas_del_dia(self, recurso_id: int, fecha: date) -> list[Reserva]:
        consulta = _con_relaciones(
            select(Reserva)
            .where(
                Reserva.recurso_id == recurso_id,
                Reserva.fecha == fecha,
                Reserva.estado.in_(ESTADOS_ACTIVOS),
            )
            .order_by(*ORDEN)
        )
        return list(self.session.scalars(consulta))

    def activas_por_dia(self, recurso_id: int, desde: date, hasta: date) -> list[tuple[date, int]]:
        consulta = (
            select(Reserva.fecha, func.count())
            .where(
                Reserva.recurso_id == recurso_id,
                Reserva.fecha.between(desde, hasta),
                Reserva.estado.in_(ESTADOS_ACTIVOS),
            )
            .group_by(Reserva.fecha)
            .order_by(Reserva.fecha)
        )
        return [(fecha, total) for fecha, total in self.session.execute(consulta)]


def get_reserva_repository(session: Annotated[Session, Depends(get_session)]) -> ReservaRepository:
    return ReservaRepository(session)
