import calendar
from collections import Counter
from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from typing import Annotated, NamedTuple

from fastapi import Depends

from app.common.enums import EstadoReserva, ModalidadReserva, PoliticaCancelacion, Rol
from app.common.errores import Conflicto, NoEncontrado, NoPermitido, ReglaIncumplida
from app.common.horas import FIN_DIA, INICIO_DIA, formato_hora
from app.recursos.dto import RecursoRespuesta, SalaReunionRespuesta
from app.recursos.service import RecursoService, get_recurso_service
from app.reservas.dto import (
    DiaOcupadoRespuesta,
    DisponibilidadRespuesta,
    FranjaRespuesta,
    ReservaCreadaRespuesta,
    ReservaPeticion,
    ReservaRespuesta,
)
from app.reservas.entity import MAX_DIAS_RESERVA, Reserva
from app.reservas.repository import ESTADOS_ACTIVOS, ReservaRepository, get_reserva_repository
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


def validar_rango(recurso: RecursoRespuesta, fecha: date, fecha_fin: date, por_horas: bool) -> None:
    """Regla 1: por horas, un solo día; día completo, de 1 a MAX_DIAS_RESERVA días seguidos."""
    if fecha_fin < fecha:
        raise ReglaIncumplida("La fecha de fin no puede ser anterior a la de inicio")
    if fecha_fin == fecha:
        return
    if por_horas or recurso.modalidad_reserva not in DIA_COMPLETO:
        raise ReglaIncumplida("Las reservas por horas son de un solo día")
    if (fecha_fin - fecha).days >= MAX_DIAS_RESERVA:
        raise ReglaIncumplida(f"Una reserva abarca como mucho {MAX_DIAS_RESERVA} días seguidos")


def solapa(inicio_a: time, fin_a: time, inicio_b: time, fin_b: time) -> bool:
    """Concepto «Solapamiento»: cubre solapes parciales, totales y una franja contenida en otra."""
    return inicio_a < fin_b and inicio_b < fin_a


class Ocupacion(NamedTuple):
    """Lo que ocupa una reserva activa en el día."""

    reserva_id: int
    inicio: time
    fin: time
    carga: int
    pendiente: bool


class Tramo(NamedTuple):
    """Un tramo del día con su ocupación, con y sin las reservas pendientes, y quién lo ocupa."""

    desde: time
    hasta: time
    carga: int
    carga_sin_pendientes: int
    ocupada_por: tuple[int, ...]


def tramos(ocupaciones: list[Ocupacion]) -> list[Tramo]:
    """Parte [00:00, 23:59) por los inicios y fines de las ocupaciones y suma la de cada tramo.

    Los tramos vecinos con los mismos ocupantes se fusionan, así que cada reserva de
    `ocupada_por` cubre el tramo entero. Responde a la regla 20 y valida las reglas 5,
    6 y 8 con la misma partición (decisiones 0013, 0016 y 0017).
    """
    cortes = sorted({INICIO_DIA, FIN_DIA} | {t for o in ocupaciones for t in (o.inicio, o.fin)})
    resultado: list[Tramo] = []
    for desde, hasta in zip(cortes, cortes[1:]):
        cubren = [o for o in ocupaciones if solapa(o.inicio, o.fin, desde, hasta)]
        carga = sum(o.carga for o in cubren)
        sin_pendientes = sum(o.carga for o in cubren if not o.pendiente)
        ids = tuple(o.reserva_id for o in cubren)
        anterior = resultado[-1] if resultado else None
        # Los mismos ocupantes dan las mismas cargas
        if anterior and anterior.ocupada_por == ids:
            resultado[-1] = anterior._replace(hasta=hasta)
        else:
            resultado.append(Tramo(desde, hasta, carga, sin_pendientes, ids))
    return resultado


def pico(tramos_del_dia: list[Tramo], inicio: time, fin: time) -> Tramo | None:
    """El tramo de más carga que se solapa con [inicio, fin); el primero si empatan."""
    solapados = [t for t in tramos_del_dia if solapa(t.desde, t.hasta, inicio, fin)]
    return max(solapados, key=lambda t: t.carga, default=None)


def inicio_de(fecha: date, hora_inicio: time | None) -> datetime:
    """Inicio de una reserva: su fecha a la hora de inicio; en día completo, a las 00:00."""
    return datetime.combine(fecha, hora_inicio or INICIO_DIA)


def puede_cancelar(politica: PoliticaCancelacion, inicio: datetime, ahora: datetime) -> bool:
    """Regla 15: Flexible hasta 1 h antes; Moderada hasta 24 h antes; Bloqueada, nunca."""
    match politica:
        case PoliticaCancelacion.FLEXIBLE:
            return ahora <= inicio - timedelta(hours=1)
        case PoliticaCancelacion.MODERADA:
            return ahora <= inicio - timedelta(hours=24)
    return False


def puede_transferir(politica: PoliticaCancelacion, inicio: datetime, ahora: datetime) -> bool:
    """Reglas 15 y 19: Flexible hasta el inicio; Moderada desde 24 h antes hasta el inicio."""
    match politica:
        case PoliticaCancelacion.FLEXIBLE:
            return ahora < inicio
        case PoliticaCancelacion.MODERADA:
            return inicio - timedelta(hours=24) < ahora < inicio
    return False


def comenzada(inicio: datetime, ahora: datetime) -> bool:
    """Regla 10: una reserva ha comenzado cuando llega su inicio."""
    return ahora >= inicio


def capacidad_compartida(recurso: RecursoRespuesta) -> int | None:
    """La capacidad de una sala con aforo compartido (regla 6); None en el resto de recursos."""
    if isinstance(recurso, SalaReunionRespuesta) and recurso.aforo_compartido:
        return recurso.capacidad_maxima
    return None


def ocupacion(reserva: Reserva, aforo: bool) -> int:
    """Lo que ocupa una reserva: sus asistentes con aforo compartido; el recurso entero sin él."""
    return (reserva.asistentes_sala or 0) if aforo else 1


def ocupaciones(reservas: list[Reserva], aforo: bool) -> list[Ocupacion]:
    return [
        Ocupacion(
            r.id,
            *franja_de(r.hora_inicio, r.hora_fin),
            ocupacion(r, aforo),
            r.estado == EstadoReserva.PENDIENTE,
        )
        for r in reservas
    ]


def pendientes_a_rechazar(
    reservas: list[Reserva],
    inicio: time,
    fin: time,
    asistentes: int | None,
    capacidad: int | None,
) -> list[Reserva]:
    """Regla 8: las pendientes que un responsable rechaza al reservar [inicio, fin), en orden.

    Sin aforo compartido cuenta como capacidad 1 con ocupación 1 por reserva, así que acaba
    rechazando todas las solapadas. Mientras no quepa, en el momento de máxima ocupación se
    rechaza la pendiente más reciente que lo ocupa. Las candidatas se buscan en un punto y no
    en el tramo, que puede ser la fusión de varias pendientes contiguas (decisión 0016).

    Precondición: la franja cabe contando solo las aprobadas de `reservas`. Así siempre hay
    candidata: si nadie pendiente ocupara el punto, su carga sería solo de aprobadas, que ya
    cabía. Y cada candidata ocupa un punto de [inicio, fin), así que se solapa con la franja.
    """
    aforo = capacidad is not None
    tope = capacidad if capacidad is not None else 1
    nueva = (asistentes or 0) if aforo else 1
    restantes = list(reservas)
    rechazadas: list[Reserva] = []
    while True:
        maximo = pico(tramos(ocupaciones(restantes, aforo)), inicio, fin)
        if maximo is None or maximo.carga + nueva <= tope:
            return rechazadas
        punto = max(maximo.desde, inicio)
        candidatas = [
            r
            for r in restantes
            if r.estado == EstadoReserva.PENDIENTE
            and (franja := franja_de(r.hora_inicio, r.hora_fin))[0] <= punto < franja[1]
        ]
        elegida = max(candidatas, key=lambda r: (r.creada_en, r.id))
        restantes.remove(elegida)
        rechazadas.append(elegida)


def reserva_a_respuesta(reserva: Reserva, ahora: datetime) -> ReservaRespuesta:
    activa = reserva.estado in ESTADOS_ACTIVOS
    politica = reserva.recurso.politica_cancelacion
    inicio = inicio_de(reserva.fecha, reserva.hora_inicio)
    return ReservaRespuesta(
        id=reserva.id,
        recurso=RecursoService.a_respuesta(reserva.recurso),
        titular=UsuarioRespuesta.model_validate(reserva.titular),
        aprobada_por=(
            UsuarioRespuesta.model_validate(reserva.aprobada_por) if reserva.aprobada_por else None
        ),
        fecha=reserva.fecha,
        fecha_fin=reserva.fecha_fin,
        hora_inicio=reserva.hora_inicio,
        hora_fin=reserva.hora_fin,
        asistentes_sala=reserva.asistentes_sala,
        estado=reserva.estado,
        creada_en=reserva.creada_en,
        puede_cancelar=activa and puede_cancelar(politica, inicio, ahora),
        puede_transferir=activa and puede_transferir(politica, inicio, ahora),
        puede_aprobar=reserva.estado == EstadoReserva.PENDIENTE and not comenzada(inicio, ahora),
    )


def describir(reserva: Reserva) -> str:
    """«09:00–10:30 de Ana García (pendiente)», para los mensajes de conflicto."""
    if reserva.fecha_fin != reserva.fecha:
        cuando = f"del {reserva.fecha:%d/%m} al {reserva.fecha_fin:%d/%m}"
    elif reserva.hora_inicio is None or reserva.hora_fin is None:
        cuando = "todo el día"
    else:
        cuando = f"{formato_hora(reserva.hora_inicio)}–{formato_hora(reserva.hora_fin)}"
    titular = f"{reserva.titular.nombre} {reserva.titular.apellidos}"
    return f"{cuando} de {titular} ({reserva.estado.lower()})"


MOTIVO_SIN_CANCELAR = {
    PoliticaCancelacion.FLEXIBLE: "Con la política flexible solo se cancela hasta 1 h antes del inicio",
    PoliticaCancelacion.MODERADA: "Con la política moderada solo se cancela hasta 24 h antes del inicio",
    PoliticaCancelacion.BLOQUEADA: "La política bloqueada no permite cancelar",
}

MOTIVO_SIN_TRANSFERIR = {
    PoliticaCancelacion.FLEXIBLE: "Con la política flexible solo se transfiere hasta el inicio",
    PoliticaCancelacion.MODERADA: (
        "Con la política moderada solo se transfiere desde 24 h antes del inicio hasta el inicio"
    ),
    PoliticaCancelacion.BLOQUEADA: "La política bloqueada no permite transferir",
}


# --- Servicios ---


class DisponibilidadService:
    def __init__(
        self,
        repositorio: ReservaRepository,
        recursos: RecursoService,
        reloj: Reloj = datetime.now,
    ):
        self.repositorio = repositorio
        self.recursos = recursos
        self.reloj = reloj

    def consultar(
        self, recurso_id: int, fecha: date, fecha_fin: date | None = None
    ) -> DisponibilidadRespuesta:
        """Regla 20. No recorta el pasado: eso lo decide quien consulta (y crear, regla 3).

        Con `fecha_fin`, la disponibilidad de día completo de todo el rango (decisión 0018).
        """
        recurso = self.recursos.obtener(recurso_id)
        fecha_fin = fecha_fin or fecha
        validar_rango(recurso, fecha, fecha_fin, por_horas=False)
        reservas = self.repositorio.activas_entre(recurso_id, fecha, fecha_fin)
        ahora = self.reloj()

        franjas = None
        if recurso.modalidad_reserva in POR_HORAS and fecha_fin == fecha:
            franjas = [self._franja(recurso, t) for t in self._tramos_del_dia(recurso, reservas)]
        dia_completo = recurso.modalidad_reserva in DIA_COMPLETO
        aprobadas = [r for r in reservas if r.estado == EstadoReserva.APROBADA]
        return DisponibilidadRespuesta(
            recurso_id=recurso_id,
            fecha=fecha,
            fecha_fin=fecha_fin,
            reservas=[reserva_a_respuesta(reserva, ahora) for reserva in reservas],
            franjas=franjas,
            dia_completo_libre=(not reservas) if dia_completo else None,
            dia_completo_libre_sin_pendientes=(not aprobadas) if dia_completo else None,
        )

    def resumen_mes(self, recurso_id: int, anio: int, mes: int) -> list[DiaOcupadoRespuesta]:
        self.recursos.obtener(recurso_id)
        desde = date(anio, mes, 1)
        hasta = date(anio, mes, calendar.monthrange(anio, mes)[1])
        # Una reserva de varios días cuenta en cada uno de sus días dentro del mes
        totales: Counter[date] = Counter()
        for primero, ultimo in self.repositorio.rangos_activos(recurso_id, desde, hasta):
            dia = max(primero, desde)
            while dia <= min(ultimo, hasta):
                totales[dia] += 1
                dia += timedelta(days=1)
        return [
            DiaOcupadoRespuesta(fecha=fecha, reservas=total)
            for fecha, total in sorted(totales.items())
        ]

    def comprobar_hueco(
        self,
        recurso: RecursoRespuesta,
        fecha: date,
        fecha_fin: date,
        inicio: time,
        fin: time,
        asistentes: int | None,
        responsable: bool,
    ) -> list[Reserva]:
        """Reglas 5, 6 y 8: lanza Conflicto si la franja no cabe con las reservas que bloquean.

        A un trabajador le bloquean todas las activas; a un responsable, solo las aprobadas, y
        devuelve las pendientes que tiene que rechazar (decisión 0016). Las reservas del rango
        quedan bloqueadas hasta el commit, para que nadie apruebe a la vez una que se rechaza.

        Con varios días, la franja es el día entero y cualquier activa del rango la solapa, así que
        basta con proyectarlas todas sobre un solo día. El aforo compartido solo existe en las
        salas, que se reservan por horas y de un día (decisión 0018).
        """
        reservas = self.repositorio.activas_entre_para_actualizar(recurso.id, fecha, fecha_fin)
        bloqueantes = (
            [r for r in reservas if r.estado == EstadoReserva.APROBADA] if responsable else reservas
        )
        capacidad = capacidad_compartida(recurso)
        if capacidad is not None:
            maximo = pico(self._tramos_del_dia(recurso, bloqueantes), inicio, fin)
            ocupados = maximo.carga if maximo else 0
            if ocupados + (asistentes or 0) > capacidad:
                raise Conflicto(
                    f"Se superaría la capacidad de {capacidad}: en el momento de más ocupación"
                    f" ya hay {ocupados} asistentes" + (" en reservas aprobadas" if responsable else "")
                )
        else:
            solapadas = [
                r for r in bloqueantes if solapa(*franja_de(r.hora_inicio, r.hora_fin), inicio, fin)
            ]
            if solapadas:
                raise Conflicto("La franja se solapa con: " + "; ".join(map(describir, solapadas)))
        if not responsable:
            return []
        return pendientes_a_rechazar(reservas, inicio, fin, asistentes, capacidad)

    @staticmethod
    def _tramos_del_dia(recurso: RecursoRespuesta, reservas: list[Reserva]) -> list[Tramo]:
        return tramos(ocupaciones(reservas, capacidad_compartida(recurso) is not None))

    @staticmethod
    def _franja(recurso: RecursoRespuesta, tramo: Tramo) -> FranjaRespuesta:
        capacidad = capacidad_compartida(recurso)
        if capacidad is not None:
            libres = capacidad - tramo.carga
            libres_sin_pendientes = capacidad - tramo.carga_sin_pendientes
            return FranjaRespuesta(
                inicio=tramo.desde,
                fin=tramo.hasta,
                libre=libres > 0,
                capacidad_libre=libres,
                libre_sin_pendientes=libres_sin_pendientes > 0,
                capacidad_libre_sin_pendientes=libres_sin_pendientes,
                ocupada_por=list(tramo.ocupada_por),
            )
        return FranjaRespuesta(
            inicio=tramo.desde,
            fin=tramo.hasta,
            libre=tramo.carga == 0,
            capacidad_libre=None,
            libre_sin_pendientes=tramo.carga_sin_pendientes == 0,
            capacidad_libre_sin_pendientes=None,
            ocupada_por=list(tramo.ocupada_por),
        )


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

    def crear(self, peticion: ReservaPeticion, usuario: UsuarioRespuesta) -> ReservaCreadaRespuesta:
        """Orden: 404 del recurso, 400 de las reglas, bloqueo del recurso y 409 de los conflictos.

        Un responsable rechaza en la misma transacción las pendientes que estorban (regla 8).
        """
        recurso = self.recursos.obtener(peticion.recurso_id)
        inicio, fin = self._validar(peticion, recurso)
        fecha_fin = peticion.ultimo_dia
        responsable = usuario.rol == Rol.RESPONSABLE

        self.repositorio.bloquear_recurso(recurso.id)
        rechazadas = self.disponibilidad.comprobar_hueco(
            recurso, peticion.fecha, fecha_fin, inicio, fin, peticion.asistentes_sala, responsable
        )
        for pendiente in rechazadas:
            pendiente.estado = EstadoReserva.RECHAZADA

        # Regla 7: un responsable reserva ya aprobada, con él mismo como aprobador
        reserva = Reserva(
            recurso_id=recurso.id,
            titular_id=usuario.id,
            aprobada_por_id=usuario.id if responsable else None,
            fecha=peticion.fecha,
            fecha_fin=fecha_fin,
            hora_inicio=peticion.hora_inicio,
            hora_fin=peticion.hora_fin,
            asistentes_sala=peticion.asistentes_sala,
            estado=EstadoReserva.APROBADA if responsable else EstadoReserva.PENDIENTE,
        )
        self.repositorio.guardar(reserva)
        self.repositorio.confirmar()
        return ReservaCreadaRespuesta(
            **dict(self._releer(reserva.id)),
            rechazadas=[self._releer(r.id) for r in rechazadas],
        )

    def aprobar(self, reserva_id: int, usuario: UsuarioRespuesta) -> ReservaRespuesta:
        """Reglas 9, 10 y 12: no vuelve a comprobar conflictos; solo un responsable reserva encima."""
        reserva = self._obtener(reserva_id, para_actualizar=True)
        self._exigir_pendiente_y_responsable(reserva, usuario, "aprobar")
        if comenzada(inicio_de(reserva.fecha, reserva.hora_inicio), self.reloj()):
            raise Conflicto("No se puede aprobar una reserva que ya ha comenzado")
        reserva.estado = EstadoReserva.APROBADA
        reserva.aprobada_por_id = usuario.id
        return self._confirmar(reserva.id)

    def rechazar(self, reserva_id: int, usuario: UsuarioRespuesta) -> ReservaRespuesta:
        """Reglas 9 y 11."""
        reserva = self._obtener(reserva_id, para_actualizar=True)
        self._exigir_pendiente_y_responsable(reserva, usuario, "rechazar")
        reserva.estado = EstadoReserva.RECHAZADA
        return self._confirmar(reserva.id)

    def cancelar(self, reserva_id: int, usuario: UsuarioRespuesta) -> ReservaRespuesta:
        """Reglas 13 a 16."""
        reserva = self._obtener(reserva_id, para_actualizar=True)
        self._exigir_titular(reserva, usuario, "cancelar")
        self._exigir_activa(reserva, "cancelar")
        politica = reserva.recurso.politica_cancelacion
        if not puede_cancelar(politica, inicio_de(reserva.fecha, reserva.hora_inicio), self.reloj()):
            raise Conflicto(MOTIVO_SIN_CANCELAR[politica])
        reserva.estado = EstadoReserva.CANCELADA
        return self._confirmar(reserva.id)

    def transferir(
        self, reserva_id: int, nuevo_titular_id: int, usuario: UsuarioRespuesta
    ) -> ReservaRespuesta:
        """Reglas 13 a 15 y 17 a 19: solo cambia el titular; el estado se mantiene."""
        reserva = self._obtener(reserva_id, para_actualizar=True)
        self.usuarios.obtener(nuevo_titular_id)
        self._exigir_titular(reserva, usuario, "transferir")
        if nuevo_titular_id == reserva.titular_id:
            raise ReglaIncumplida("No se puede transferir una reserva a su propio titular")
        self._exigir_activa(reserva, "transferir")
        politica = reserva.recurso.politica_cancelacion
        inicio = inicio_de(reserva.fecha, reserva.hora_inicio)
        if not puede_transferir(politica, inicio, self.reloj()):
            raise Conflicto(MOTIVO_SIN_TRANSFERIR[politica])
        reserva.titular_id = nuevo_titular_id
        return self._confirmar(reserva.id)

    def obtener(self, reserva_id: int, usuario: UsuarioRespuesta) -> ReservaRespuesta:
        """El titular o un responsable; las activas ya son públicas en la disponibilidad (decisión 0015)."""
        reserva = self._obtener(reserva_id)
        if reserva.titular_id != usuario.id and usuario.rol != Rol.RESPONSABLE:
            raise NoPermitido("Solo el titular o un responsable pueden ver la reserva")
        return reserva_a_respuesta(reserva, self.reloj())

    def mias(self, usuario: UsuarioRespuesta) -> list[ReservaRespuesta]:
        ahora = self.reloj()
        return [reserva_a_respuesta(r, ahora) for r in self.repositorio.de_titular(usuario.id)]

    def pendientes(self, usuario: UsuarioRespuesta) -> list[ReservaRespuesta]:
        """Todas las pendientes, también las de fechas pasadas: la regla 9 no las excluye."""
        if usuario.rol != Rol.RESPONSABLE:
            raise NoPermitido("Solo un responsable puede ver las reservas por aprobar")
        ahora = self.reloj()
        return [reserva_a_respuesta(r, ahora) for r in self.repositorio.pendientes()]

    def _validar(self, peticion: ReservaPeticion, recurso: RecursoRespuesta) -> tuple[time, time]:
        """Reglas 1 a 4. Devuelve la franja de la reserva."""
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
        validar_rango(recurso, peticion.fecha, peticion.ultimo_dia, por_horas)

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

    def _obtener(self, reserva_id: int, para_actualizar: bool = False) -> Reserva:
        """La reserva o 404; bloqueada hasta el commit si se va a modificar (decisión 0013)."""
        if para_actualizar:
            reserva = self.repositorio.obtener_para_actualizar(reserva_id)
        else:
            reserva = self.repositorio.obtener(reserva_id)
        if reserva is None:
            raise NoEncontrado(f"No existe la reserva {reserva_id}")
        return reserva

    @staticmethod
    def _exigir_pendiente_y_responsable(
        reserva: Reserva, usuario: UsuarioRespuesta, accion: str
    ) -> None:
        if usuario.rol != Rol.RESPONSABLE:
            raise NoPermitido(f"Solo un responsable puede {accion} reservas")
        if reserva.estado != EstadoReserva.PENDIENTE:
            raise Conflicto(
                f"Solo se pueden {accion} reservas pendientes; esta está {reserva.estado.lower()}"
            )

    @staticmethod
    def _exigir_titular(reserva: Reserva, usuario: UsuarioRespuesta, accion: str) -> None:
        if reserva.titular_id != usuario.id:
            raise NoPermitido(f"Solo el titular puede {accion} la reserva")

    @staticmethod
    def _exigir_activa(reserva: Reserva, accion: str) -> None:
        if reserva.estado not in ESTADOS_ACTIVOS:
            raise Conflicto(
                f"Solo se pueden {accion} reservas activas; esta está {reserva.estado.lower()}"
            )

    def _confirmar(self, reserva_id: int) -> ReservaRespuesta:
        self.repositorio.confirmar()
        return self._releer(reserva_id)

    def _releer(self, reserva_id: int) -> ReservaRespuesta:
        """Relee la reserva ya confirmada, para que `creada_en` y las relaciones estén cargados."""
        reserva = self.repositorio.obtener(reserva_id)
        assert reserva is not None
        return reserva_a_respuesta(reserva, self.reloj())


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
