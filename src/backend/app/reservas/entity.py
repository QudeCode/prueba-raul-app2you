from datetime import date, datetime, time

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import EstadoReserva
from app.database import Base, check_enum, tipo_enum
from app.recursos.entity import Recurso
from app.usuarios.entity import Usuario


class Reserva(Base):
    """Las reglas que cruzan tablas (modalidad según el tipo, asistentes) van en el servicio."""

    __tablename__ = "reserva"
    __table_args__ = (
        check_enum("estado", EstadoReserva, "ck_reserva_estado"),
        CheckConstraint(
            "(hora_inicio IS NULL) = (hora_fin IS NULL)", name="ck_reserva_horas_juntas"
        ),
        CheckConstraint("hora_inicio < hora_fin", name="ck_reserva_horas_orden"),
        # Regla 2: TIME admite 24:00 en PostgreSQL, pero Python no puede leerlo (decisión 0004)
        CheckConstraint("hora_fin <= '23:59'", name="ck_reserva_hora_fin_maxima"),
        # Regla 2: las horas van en minutos, sin segundos
        CheckConstraint(
            "(hora_inicio IS NULL OR EXTRACT(SECOND FROM hora_inicio) = 0)"
            " AND (hora_fin IS NULL OR EXTRACT(SECOND FROM hora_fin) = 0)",
            name="ck_reserva_horas_en_minutos",
        ),
        CheckConstraint(
            "asistentes_sala IS NULL OR asistentes_sala >= 1", name="ck_reserva_asistentes"
        ),
        CheckConstraint(
            f"estado <> '{EstadoReserva.APROBADA}' OR aprobada_por_id IS NOT NULL",
            name="ck_reserva_aprobada_con_aprobador",
        ),
        Index("ix_reserva_recurso_fecha", "recurso_id", "fecha"),
        Index("ix_reserva_titular", "titular_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    recurso_id: Mapped[int] = mapped_column(ForeignKey("recurso.id"))
    titular_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    aprobada_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))
    fecha: Mapped[date]
    hora_inicio: Mapped[time | None]
    hora_fin: Mapped[time | None]
    asistentes_sala: Mapped[int | None]
    estado: Mapped[EstadoReserva] = mapped_column(tipo_enum(EstadoReserva))
    creada_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    recurso: Mapped[Recurso] = relationship()
    titular: Mapped[Usuario] = relationship(foreign_keys=[titular_id])
    aprobada_por: Mapped[Usuario | None] = relationship(foreign_keys=[aprobada_por_id])
