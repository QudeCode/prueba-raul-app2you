from datetime import date
from typing import Annotated

from fastapi import Depends
from sqlalchemy import ColumnElement, Select, select
from sqlalchemy.orm import Session, joinedload

from app.common.enums import EstadoReserva
from app.database import get_session
from app.recursos.entity import Recurso
from app.reservas.entity import Reserva

# Solo las activas ocupan el recurso (reglas de negocio, «Reserva activa»)
ESTADOS_ACTIVOS = (EstadoReserva.PENDIENTE, EstadoReserva.APROBADA)

# Por fecha y hora; los días completos (sin hora) primero
ORDEN = (Reserva.fecha, Reserva.hora_inicio.asc().nulls_first(), Reserva.id)


def _con_relaciones(consulta: Select[tuple[Reserva]]) -> Select[tuple[Reserva]]:
    return consulta.options(
        joinedload(Reserva.recurso), joinedload(Reserva.titular), joinedload(Reserva.aprobada_por)
    )


def _activas_entre(desde: date, hasta: date) -> tuple[ColumnElement[bool], ...]:
    """Las activas que ocupan algún día de [desde, hasta]: sus rangos de fechas se solapan."""
    return (
        Reserva.fecha <= hasta,
        Reserva.fecha_fin >= desde,
        Reserva.estado.in_(ESTADOS_ACTIVOS),
    )


def _consulta_activas_entre(recurso_id: int, desde: date, hasta: date) -> Select[tuple[Reserva]]:
    return _con_relaciones(
        select(Reserva)
        .where(Reserva.recurso_id == recurso_id, *_activas_entre(desde, hasta))
        .order_by(*ORDEN)
    )


class ReservaRepository:
    def __init__(self, session: Session):
        self.session = session

    def obtener(self, reserva_id: int) -> Reserva | None:
        consulta = _con_relaciones(select(Reserva).where(Reserva.id == reserva_id))
        return self.session.scalars(consulta).first()

    def obtener_para_actualizar(self, reserva_id: int) -> Reserva | None:
        """Bloquea la fila hasta el commit: dos acciones sobre la misma reserva van una tras otra (decisión 0013)."""
        consulta = (
            select(Reserva)
            .where(Reserva.id == reserva_id)
            .with_for_update(of=Reserva)
            .execution_options(populate_existing=True)
        )
        return self.session.scalars(consulta).first()

    def activas_entre(self, recurso_id: int, desde: date, hasta: date) -> list[Reserva]:
        return list(self.session.scalars(_consulta_activas_entre(recurso_id, desde, hasta)))

    def activas_entre_para_actualizar(
        self, recurso_id: int, desde: date, hasta: date
    ) -> list[Reserva]:
        """Bloquea las filas hasta el commit: nadie aprueba una pendiente que se va a rechazar (decisión 0016)."""
        consulta = (
            _consulta_activas_entre(recurso_id, desde, hasta)
            .with_for_update(of=Reserva)
            .execution_options(populate_existing=True)
        )
        return list(self.session.scalars(consulta))

    def rangos_activos(self, recurso_id: int, desde: date, hasta: date) -> list[tuple[date, date]]:
        """Primer y último día de cada activa que ocupa algún día de [desde, hasta]."""
        consulta = select(Reserva.fecha, Reserva.fecha_fin).where(
            Reserva.recurso_id == recurso_id, *_activas_entre(desde, hasta)
        )
        return [(fecha, fecha_fin) for fecha, fecha_fin in self.session.execute(consulta)]

    def de_titular(self, usuario_id: int) -> list[Reserva]:
        consulta = _con_relaciones(
            select(Reserva).where(Reserva.titular_id == usuario_id).order_by(*ORDEN)
        )
        return list(self.session.scalars(consulta))

    def pendientes(self) -> list[Reserva]:
        consulta = _con_relaciones(
            select(Reserva).where(Reserva.estado == EstadoReserva.PENDIENTE).order_by(*ORDEN)
        )
        return list(self.session.scalars(consulta))

    def bloquear_recurso(self, recurso_id: int) -> None:
        """Serializa las reservas de un recurso hasta el commit (decisión 0013)."""
        self.session.execute(select(Recurso.id).where(Recurso.id == recurso_id).with_for_update())

    def guardar(self, reserva: Reserva) -> None:
        self.session.add(reserva)
        self.session.flush()

    def confirmar(self) -> None:
        self.session.commit()


def get_reserva_repository(session: Annotated[Session, Depends(get_session)]) -> ReservaRepository:
    return ReservaRepository(session)
