import calendar
from collections.abc import Callable
from datetime import date, datetime, time
from typing import Annotated

from fastapi import Depends

from app.common.enums import EstadoReserva, ModalidadReserva, Rol
from app.common.errores import Conflicto, ReglaIncumplida
from app.common.horas import FIN_DIA, INICIO_DIA, formato_hora
from app.recursos.dto import RecursoRespuesta, SalaReunionRespuesta
from app.recursos.service import RecursoService, get_recurso_service
from app.reservas.dto import (
    DiaOcupadoRespuesta,
    DisponibilidadRespuesta,
    FranjaRespuesta,
    ReservaPeticion,
    ReservaRespuesta,
)
from app.reservas.entity import Reserva
from app.reservas.repository import ReservaRepository, get_reserva_repository
from app.usuarios.dto import UsuarioRespuesta
from app.usuarios.service import UsuarioService, get_usuario_service

Reloj = Callable[[], datetime]

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


def inicio_de(fecha: date, hora_inicio: time | None) -> datetime:
    """Inicio de una reserva: su fecha a la hora de inicio; en día completo, a las 00:00."""
    return datetime.combine(fecha, hora_inicio or INICIO_DIA)


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


def describir(reserva: Reserva) -> str:
    """«09:00–10:30 de Ana García (pendiente)», para los mensajes de conflicto."""
    if reserva.hora_inicio is None or reserva.hora_fin is None:
        cuando = "todo el día"
    else:
        cuando = f"{formato_hora(reserva.hora_inicio)}–{formato_hora(reserva.hora_fin)}"
    titular = f"{reserva.titular.nombre} {reserva.titular.apellidos}"
    return f"{cuando} de {titular} ({reserva.estado.lower()})"


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

    def comprobar_hueco(
        self,
        recurso: RecursoRespuesta,
        fecha: date,
        inicio: time,
        fin: time,
        asistentes: int | None,
    ) -> None:
        """Reglas 5 y 6: lanza Conflicto si la franja no cabe con las reservas activas del día."""
        reservas = self.repositorio.activas_del_dia(recurso.id, fecha)
        capacidad = capacidad_compartida(recurso)
        if capacidad is not None:
            pico = max(
                (c for d, h, c in self._tramos_del_dia(recurso, reservas) if d < fin and inicio < h),
                default=0,
            )
            if pico + (asistentes or 0) > capacidad:
                raise Conflicto(
                    f"Se superaría la capacidad de {capacidad}: en el momento de más ocupación"
                    f" ya hay {pico} asistentes"
                )
            return
        solapadas = [
            reserva
            for reserva in reservas
            if (franja := franja_de(reserva.hora_inicio, reserva.hora_fin))[0] < fin
            and inicio < franja[1]
        ]
        if solapadas:
            raise Conflicto("La franja se solapa con: " + "; ".join(map(describir, solapadas)))

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


class ReservaService:
    def __init__(
        self,
        repositorio: ReservaRepository,
        recursos: RecursoService,
        usuarios: UsuarioService,
        disponibilidad: DisponibilidadService,
        reloj: Reloj = datetime.now,
    ):
        self.repositorio = repositorio
        self.recursos = recursos
        self.usuarios = usuarios
        self.disponibilidad = disponibilidad
        self.reloj = reloj

    def crear(self, peticion: ReservaPeticion, usuario: UsuarioRespuesta) -> ReservaRespuesta:
        """Orden: 404 del recurso, 400 de las reglas, bloqueo del recurso y 409 de los conflictos."""
        recurso = self.recursos.obtener(peticion.recurso_id)
        inicio, fin = self._validar(peticion, recurso)

        self.repositorio.bloquear_recurso(recurso.id)
        self.disponibilidad.comprobar_hueco(
            recurso, peticion.fecha, inicio, fin, peticion.asistentes_sala
        )

        # Regla 7: un responsable reserva ya aprobada, con él mismo como aprobador
        responsable = usuario.rol == Rol.RESPONSABLE
        reserva = Reserva(
            recurso_id=recurso.id,
            titular_id=usuario.id,
            aprobada_por_id=usuario.id if responsable else None,
            fecha=peticion.fecha,
            hora_inicio=peticion.hora_inicio,
            hora_fin=peticion.hora_fin,
            asistentes_sala=peticion.asistentes_sala,
            estado=EstadoReserva.APROBADA if responsable else EstadoReserva.PENDIENTE,
        )
        self.repositorio.guardar(reserva)
        return self._confirmar(reserva.id)

    def mias(self, usuario: UsuarioRespuesta) -> list[ReservaRespuesta]:
        return [reserva_a_respuesta(r) for r in self.repositorio.de_titular(usuario.id)]

    def _validar(self, peticion: ReservaPeticion, recurso: RecursoRespuesta) -> tuple[time, time]:
        """Reglas 2, 3 y 4. Devuelve la franja de la reserva."""
        hora_inicio, hora_fin = peticion.hora_inicio, peticion.hora_fin
        if (hora_inicio is None) != (hora_fin is None):
            raise ReglaIncumplida(
                "Indica la hora de inicio y la de fin, o ninguna para reservar el día completo"
            )
        por_horas = hora_inicio is not None
        if por_horas and recurso.modalidad_reserva not in POR_HORAS:
            raise ReglaIncumplida(f"{recurso.nombre} solo se reserva por días completos")
        if not por_horas and recurso.modalidad_reserva not in DIA_COMPLETO:
            raise ReglaIncumplida(f"{recurso.nombre} solo se reserva por horas")
        if hora_inicio is not None and hora_fin is not None and hora_inicio >= hora_fin:
            raise ReglaIncumplida("La hora de inicio debe ser anterior a la de fin")

        if inicio_de(peticion.fecha, hora_inicio) <= self.reloj():
            raise ReglaIncumplida("No se puede reservar en el pasado")

        asistentes = peticion.asistentes_sala
        capacidad = capacidad_compartida(recurso)
        if capacidad is not None:
            if asistentes is None or not 1 <= asistentes <= capacidad:
                raise ReglaIncumplida(f"Indica entre 1 y {capacidad} asistentes")
        elif asistentes is not None:
            raise ReglaIncumplida("Los asistentes solo se indican en salas con aforo compartido")

        return franja_de(hora_inicio, hora_fin)

    def _confirmar(self, reserva_id: int) -> ReservaRespuesta:
        """Confirma y relee la reserva, para que `creada_en` y las relaciones estén cargados."""
        self.repositorio.confirmar()
        reserva = self.repositorio.obtener(reserva_id)
        assert reserva is not None
        return reserva_a_respuesta(reserva)


def get_disponibilidad_service(
    repositorio: Annotated[ReservaRepository, Depends(get_reserva_repository)],
    recursos: Annotated[RecursoService, Depends(get_recurso_service)],
) -> DisponibilidadService:
    return DisponibilidadService(repositorio, recursos)


def get_reserva_service(
    repositorio: Annotated[ReservaRepository, Depends(get_reserva_repository)],
    recursos: Annotated[RecursoService, Depends(get_recurso_service)],
    usuarios: Annotated[UsuarioService, Depends(get_usuario_service)],
    disponibilidad: Annotated[DisponibilidadService, Depends(get_disponibilidad_service)],
) -> ReservaService:
    return ReservaService(repositorio, recursos, usuarios, disponibilidad)
