from datetime import date, datetime

from pydantic import BaseModel

from app.common.enums import EstadoReserva
from app.common.horas import HoraMinuto
from app.recursos.dto import RecursoRespuesta
from app.usuarios.dto import UsuarioRespuesta


class ReservaPeticion(BaseModel):
    """Sin horas es día completo; con las dos, por horas (decisión 0012)."""

    recurso_id: int
    fecha: date
    hora_inicio: HoraMinuto | None = None
    hora_fin: HoraMinuto | None = None
    # Sin `ge`: la regla 4 la valida el servicio (400)
    asistentes_sala: int | None = None


class TransferenciaPeticion(BaseModel):
    nuevo_titular_id: int


class ReservaRespuesta(BaseModel):
    id: int
    recurso: RecursoRespuesta
    titular: UsuarioRespuesta
    aprobada_por: UsuarioRespuesta | None
    fecha: date
    hora_inicio: HoraMinuto | None
    hora_fin: HoraMinuto | None
    asistentes_sala: int | None
    estado: EstadoReserva
    creada_en: datetime
    # Estado y plazos al construir la respuesta (de la política, o el inicio para aprobar);
    # no comprueban el titular ni el rol
    puede_cancelar: bool
    puede_transferir: bool
    puede_aprobar: bool


class FranjaRespuesta(BaseModel):
    inicio: HoraMinuto
    fin: HoraMinuto
    libre: bool
    capacidad_libre: int | None


class DisponibilidadRespuesta(BaseModel):
    recurso_id: int
    fecha: date
    reservas: list[ReservaRespuesta]
    franjas: list[FranjaRespuesta] | None
    dia_completo_libre: bool | None


class DiaOcupadoRespuesta(BaseModel):
    fecha: date
    reservas: int
