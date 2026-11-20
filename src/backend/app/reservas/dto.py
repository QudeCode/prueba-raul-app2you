from datetime import date, datetime

from pydantic import BaseModel

from app.common.enums import EstadoReserva
from app.common.horas import HoraMinuto
from app.recursos.dto import RecursoRespuesta
from app.usuarios.dto import UsuarioRespuesta


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
