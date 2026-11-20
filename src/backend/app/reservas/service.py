import calendar
from datetime import date, time
from typing import Annotated

from fastapi import Depends

from app.common.enums import ModalidadReserva
from app.common.horas import FIN_DIA, INICIO_DIA
from app.recursos.dto import RecursoRespuesta, SalaReunionRespuesta
from app.recursos.service import RecursoService, get_recurso_service
from app.reservas.dto import (
    DiaOcupadoRespuesta,
    DisponibilidadRespuesta,
    FranjaRespuesta,
    ReservaRespuesta,
)
from app.reservas.entity import Reserva
from app.reservas.repository import ReservaRepository, get_reserva_repository
from app.usuarios.dto import UsuarioRespuesta

POR_HORAS = (ModalidadReserva.POR_HORAS, ModalidadReserva.AMBAS)
DIA_COMPLETO = (ModalidadReserva.DIA_COMPLETO, ModalidadReserva.AMBAS)

# --- Funciones puras: sin sesión ni reloj ---


def franja_de(hora_inicio: time | None, hora_fin: time | None) -> tuple[time, time]:
    """La franja dentro de la ventana [00:00, 23:59); el día completo la ocupa entera (decisión 0013)."""
    if hora_inicio is None or hora_fin is None:
        return INICIO_DIA, FIN_DIA
    return hora_inicio, hora_fin


def tramos(ocupaciones: list[tuple[time, time, int]]) -> list[tuple[time, time, int]]:
    """Parte [00:00, 23:59) por los inicios y fines de las ocupaciones y suma la de cada tramo.

    Los tramos vecinos con la misma ocupación se fusionan. Responde a la regla 20 y valida
    las reglas 5 y 6 con la misma partición (decisión 0013).
    """
    cortes = sorted({INICIO_DIA, FIN_DIA} | {t for i, f, _ in ocupaciones for t in (i, f)})
    resultado: list[tuple[time, time, int]] = []
    for desde, hasta in zip(cortes, cortes[1:]):
        carga = sum(o for inicio, fin, o in ocupaciones if inicio < hasta and desde < fin)
        if resultado and resultado[-1][2] == carga:
            resultado[-1] = (resultado[-1][0], hasta, carga)
        else:
            resultado.append((desde, hasta, carga))
    return resultado


def capacidad_compartida(recurso: RecursoRespuesta) -> int | None:
    """La capacidad de una sala con aforo compartido (regla 6); None en el resto de recursos."""
    if isinstance(recurso, SalaReunionRespuesta) and recurso.aforo_compartido:
        return recurso.capacidad_maxima
    return None


def ocupacion(reserva: Reserva, aforo: bool) -> int:
    """Lo que ocupa una reserva: sus asistentes con aforo compartido; el recurso entero sin él."""
    return (reserva.asistentes_sala or 0) if aforo else 1


def reserva_a_respuesta(reserva: Reserva) -> ReservaRespuesta:
    return ReservaRespuesta(
        id=reserva.id,
        recurso=RecursoService.a_respuesta(reserva.recurso),
        titular=UsuarioRespuesta.model_validate(reserva.titular),
        aprobada_por=(
            UsuarioRespuesta.model_validate(reserva.aprobada_por) if reserva.aprobada_por else None
        ),
        fecha=reserva.fecha,
        hora_inicio=reserva.hora_inicio,
        hora_fin=reserva.hora_fin,
        asistentes_sala=reserva.asistentes_sala,
        estado=reserva.estado,
        creada_en=reserva.creada_en,
    )


# --- Servicios ---


class DisponibilidadService:
    def __init__(
        self,
        repositorio: ReservaRepository,
        recursos: RecursoService,
    ):
        self.repositorio = repositorio
        self.recursos = recursos

    def consultar(self, recurso_id: int, fecha: date) -> DisponibilidadRespuesta:
        """Regla 20. No recorta el pasado: eso lo decide quien consulta (y crear, regla 3)."""
        recurso = self.recursos.obtener(recurso_id)
        reservas = self.repositorio.activas_del_dia(recurso_id, fecha)

        franjas = None
        if recurso.modalidad_reserva in POR_HORAS:
            franjas = [
                self._franja(recurso, desde, hasta, carga)
                for desde, hasta, carga in self._tramos_del_dia(recurso, reservas)
            ]
        return DisponibilidadRespuesta(
            recurso_id=recurso_id,
            fecha=fecha,
            reservas=[reserva_a_respuesta(reserva) for reserva in reservas],
            franjas=franjas,
            dia_completo_libre=(not reservas) if recurso.modalidad_reserva in DIA_COMPLETO else None,
        )

    def resumen_mes(self, recurso_id: int, anio: int, mes: int) -> list[DiaOcupadoRespuesta]:
        self.recursos.obtener(recurso_id)
        desde = date(anio, mes, 1)
        hasta = date(anio, mes, calendar.monthrange(anio, mes)[1])
        return [
            DiaOcupadoRespuesta(fecha=fecha, reservas=total)
            for fecha, total in self.repositorio.activas_por_dia(recurso_id, desde, hasta)
        ]

    def _tramos_del_dia(
        self, recurso: RecursoRespuesta, reservas: list[Reserva]
    ) -> list[tuple[time, time, int]]:
        aforo = capacidad_compartida(recurso) is not None
        return tramos(
            [(*franja_de(r.hora_inicio, r.hora_fin), ocupacion(r, aforo)) for r in reservas]
        )

    @staticmethod
    def _franja(recurso: RecursoRespuesta, desde: time, hasta: time, carga: int) -> FranjaRespuesta:
        capacidad = capacidad_compartida(recurso)
        if capacidad is not None:
            libres = capacidad - carga
            return FranjaRespuesta(inicio=desde, fin=hasta, libre=libres > 0, capacidad_libre=libres)
        return FranjaRespuesta(inicio=desde, fin=hasta, libre=carga == 0, capacidad_libre=None)


def get_disponibilidad_service(
    repositorio: Annotated[ReservaRepository, Depends(get_reserva_repository)],
    recursos: Annotated[RecursoService, Depends(get_recurso_service)],
) -> DisponibilidadService:
    return DisponibilidadService(repositorio, recursos)
