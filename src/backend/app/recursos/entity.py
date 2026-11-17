from typing import ClassVar

from sqlalchemy import CheckConstraint, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.common.enums import ModalidadReserva, PoliticaCancelacion, TipoRecurso
from app.database import Base, check_enum, tipo_enum

SALA = TipoRecurso.SALA_REUNION
VEHICULO = TipoRecurso.VEHICULO
EQUIPO = TipoRecurso.EQUIPO


class Recurso(Base):
    """Herencia de tabla única: los campos propios de cada tipo van vacíos en los demás (decisión 0005)."""

    __tablename__ = "recurso"
    __table_args__ = (
        check_enum("tipo", TipoRecurso, "ck_recurso_tipo"),
        check_enum("politica_cancelacion", PoliticaCancelacion, "ck_recurso_politica"),
        CheckConstraint(
            f"(tipo = '{SALA}' AND capacidad_maxima IS NOT NULL AND aforo_compartido IS NOT NULL"
            " AND matricula IS NULL AND plazas IS NULL AND numero_serie IS NULL)"
            f" OR (tipo = '{VEHICULO}' AND matricula IS NOT NULL AND plazas IS NOT NULL"
            " AND capacidad_maxima IS NULL AND aforo_compartido IS NULL AND numero_serie IS NULL)"
            f" OR (tipo = '{EQUIPO}' AND numero_serie IS NOT NULL AND capacidad_maxima IS NULL"
            " AND aforo_compartido IS NULL AND matricula IS NULL AND plazas IS NULL)",
            name="ck_recurso_campos_tipo",
        ),
        CheckConstraint(
            "capacidad_maxima IS NULL OR capacidad_maxima > 0", name="ck_recurso_capacidad"
        ),
        CheckConstraint("plazas IS NULL OR plazas > 0", name="ck_recurso_plazas"),
        UniqueConstraint("matricula", name="uq_recurso_matricula"),
        UniqueConstraint("numero_serie", name="uq_recurso_numero_serie"),
    )
    __mapper_args__ = {"polymorphic_on": "tipo"}

    MODALIDAD_RESERVA: ClassVar[ModalidadReserva]
    IMAGEN: ClassVar[str]

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[TipoRecurso] = mapped_column(tipo_enum(TipoRecurso))
    nombre: Mapped[str]
    descripcion: Mapped[str] = mapped_column(Text)
    politica_cancelacion: Mapped[PoliticaCancelacion] = mapped_column(
        tipo_enum(PoliticaCancelacion)
    )
    capacidad_maxima: Mapped[int | None]
    aforo_compartido: Mapped[bool | None]
    matricula: Mapped[str | None]
    plazas: Mapped[int | None]
    numero_serie: Mapped[str | None]


class SalaReunion(Recurso):
    __mapper_args__ = {"polymorphic_identity": TipoRecurso.SALA_REUNION}

    MODALIDAD_RESERVA = ModalidadReserva.POR_HORAS
    IMAGEN = "sala.png"


class Vehiculo(Recurso):
    __mapper_args__ = {"polymorphic_identity": TipoRecurso.VEHICULO}

    MODALIDAD_RESERVA = ModalidadReserva.DIA_COMPLETO
    IMAGEN = "vehiculo.png"


class Equipo(Recurso):
    __mapper_args__ = {"polymorphic_identity": TipoRecurso.EQUIPO}

    MODALIDAD_RESERVA = ModalidadReserva.AMBAS
    IMAGEN = "equipo.png"
