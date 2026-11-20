"""Datos de prueba: borra y vuelve a crear las tablas (python -m app.seed)."""

import random
import sys
from collections import Counter
from datetime import date, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.enums import EstadoReserva, ModalidadReserva, PoliticaCancelacion, Rol
from app.common.errores import ErrorDominio
from app.database import SessionLocal, engine, recrear_esquema
from app.entidades import Equipo, Reserva, SalaReunion, Usuario, Vehiculo
from app.recursos.dto import RecursoRespuesta
from app.recursos.repository import RecursoRepository
from app.recursos.service import RecursoService
from app.reservas.dto import ReservaPeticion, ReservaRespuesta
from app.reservas.repository import ESTADOS_ACTIVOS, ReservaRepository
from app.reservas.service import (
    POR_HORAS,
    DisponibilidadService,
    ReservaService,
    capacidad_compartida,
)
from app.usuarios.dto import UsuarioRespuesta
from app.usuarios.repository import UsuarioRepository
from app.usuarios.service import UsuarioService

FLEXIBLE = PoliticaCancelacion.FLEXIBLE
MODERADA = PoliticaCancelacion.MODERADA
BLOQUEADA = PoliticaCancelacion.BLOQUEADA


def cargar_datos(session: Session) -> None:
    """Añade los usuarios y recursos de prueba, sin hacer commit."""
    session.add_all(
        [
            Usuario(nombre="Ana", apellidos="García", rol=Rol.TRABAJADOR),
            Usuario(nombre="Luis", apellidos="Pérez", rol=Rol.TRABAJADOR),
            Usuario(nombre="Marta", apellidos="López", rol=Rol.RESPONSABLE),
            Usuario(nombre="Jordi", apellidos="Puig", rol=Rol.RESPONSABLE),
        ]
    )
    session.add_all(
        [
            SalaReunion(
                nombre="Sala Mar",
                descripcion="Sala luminosa con pantalla y videoconferencia.",
                politica_cancelacion=FLEXIBLE,
                capacidad_maxima=10,
                aforo_compartido=True,
            ),
            SalaReunion(
                nombre="Sala Montaña",
                descripcion="Sala pequeña para reuniones de equipo.",
                politica_cancelacion=MODERADA,
                capacidad_maxima=6,
                aforo_compartido=False,
            ),
            SalaReunion(
                nombre="Auditorio",
                descripcion="Espacio para presentaciones y formaciones.",
                politica_cancelacion=BLOQUEADA,
                capacidad_maxima=50,
                aforo_compartido=True,
            ),
            Vehiculo(
                nombre="Furgoneta 1",
                descripcion="Furgoneta de carga para material y mudanzas.",
                politica_cancelacion=MODERADA,
                matricula="4821 LKM",
                plazas=3,
            ),
            Vehiculo(
                nombre="Coche eléctrico",
                descripcion="Turismo eléctrico para visitas a clientes.",
                politica_cancelacion=FLEXIBLE,
                matricula="7306 MRT",
                plazas=5,
            ),
            Equipo(
                nombre="Proyector portátil",
                descripcion="Proyector con cable HDMI y mando.",
                politica_cancelacion=FLEXIBLE,
                numero_serie="PRY-2041",
            ),
            Equipo(
                nombre="Portátil de préstamo",
                descripcion="Portátil con el software corporativo instalado.",
                politica_cancelacion=MODERADA,
                numero_serie="PRT-1187",
            ),
            Equipo(
                nombre="Cámara de vídeo",
                descripcion="Cámara con trípode y micrófono para grabaciones.",
                politica_cancelacion=BLOQUEADA,
                numero_serie="CAM-0532",
            ),
        ]
    )


def peticion_aleatoria(
    aleatorio: random.Random, recurso: RecursoRespuesta, fecha: date
) -> ReservaPeticion:
    """Por horas: inicio en punto o y media entre las 08:00 y las 18:00, de 1 a 3 h.

    Día completo: una de cada tres abarca de 2 a 4 días seguidos (regla 1).
    """
    modalidad = recurso.modalidad_reserva
    if modalidad == ModalidadReserva.AMBAS:
        modalidad = aleatorio.choice([ModalidadReserva.POR_HORAS, ModalidadReserva.DIA_COMPLETO])
    if modalidad == ModalidadReserva.DIA_COMPLETO:
        dias_extra = aleatorio.randint(1, 3) if aleatorio.random() < 1 / 3 else 0
        return ReservaPeticion(
            recurso_id=recurso.id, fecha=fecha, fecha_fin=fecha + timedelta(days=dias_extra)
        )

    inicio = 8 * 60 + 30 * aleatorio.randint(0, 20)
    fin = inicio + 60 * aleatorio.randint(1, 3)
    asistentes = None
    if (capacidad := capacidad_compartida(recurso)) is not None:
        asistentes = aleatorio.randint(1, capacidad // 2)
    return ReservaPeticion(
        recurso_id=recurso.id,
        fecha=fecha,
        hora_inicio=time(inicio // 60, inicio % 60),
        hora_fin=time(fin // 60, fin % 60),
        asistentes_sala=asistentes,
    )


def generar_reservas(session: Session, aleatorio: random.Random) -> Counter[EstadoReserva]:
    """Reservas de mañana a 21 días después, creadas con el servicio para que cumplan las reglas.

    Necesita los usuarios y recursos ya confirmados: el servicio confirma cada reserva.
    """
    recursos_service = RecursoService(RecursoRepository(session))
    usuarios_service = UsuarioService(UsuarioRepository(session))
    repositorio = ReservaRepository(session)
    disponibilidad = DisponibilidadService(repositorio, recursos_service)
    reservas = ReservaService(repositorio, recursos_service, usuarios_service, disponibilidad)

    usuarios = usuarios_service.listar()
    responsables = [usuario for usuario in usuarios if usuario.rol == Rol.RESPONSABLE]
    recursos = recursos_service.listar()
    hoy = date.today()

    creadas: dict[int, ReservaRespuesta] = {}
    for dias in range(1, 22):
        fecha = hoy + timedelta(days=dias)
        for recurso in recursos:
            if aleatorio.random() >= 0.35:
                continue
            for _ in range(aleatorio.randint(1, 3)):
                peticion = peticion_aleatoria(aleatorio, recurso, fecha)
                try:
                    reserva = reservas.crear(peticion, aleatorio.choice(usuarios))
                except ErrorDominio:
                    continue  # el hueco ya estaba ocupado
                creadas[reserva.id] = reserva
                # Un responsable puede haber rechazado pendientes (regla 8): no se aprueban luego
                for rechazada in reserva.rechazadas:
                    creadas[rechazada.id] = rechazada

    # De cada diez pendientes, aprueba cinco, rechaza dos y deja tres para «Por aprobar»; por
    # posición y no al azar, para que siempre queden pendientes
    pendientes = [r for r in creadas.values() if r.estado == EstadoReserva.PENDIENTE]
    aleatorio.shuffle(pendientes)
    for indice, reserva in enumerate(pendientes):
        responsable = responsables[indice % len(responsables)]
        if indice % 10 < 5:
            creadas[reserva.id] = reservas.aprobar(reserva.id, responsable)
        elif indice % 10 < 7:
            creadas[reserva.id] = reservas.rechazar(reserva.id, responsable)

    # Cancela dos y transfiere una entre las que su política aún lo permite; si no hay, se omite
    activas = [r for r in creadas.values() if r.estado in ESTADOS_ACTIVOS]
    aleatorio.shuffle(activas)
    canceladas = [r.id for r in activas if r.puede_cancelar][:2]
    for reserva_id in canceladas:
        creadas[reserva_id] = reservas.cancelar(reserva_id, creadas[reserva_id].titular)
    for reserva in [r for r in activas if r.puede_transferir and r.id not in canceladas][:1]:
        nuevo = next(usuario for usuario in usuarios if usuario.id != reserva.titular.id)
        creadas[reserva.id] = reservas.transferir(reserva.id, nuevo.id, reserva.titular)

    insertar_reservas_pasadas(session, recursos, usuarios, hoy)
    session.commit()
    return Counter(session.scalars(select(Reserva.estado)))


def insertar_reservas_pasadas(
    session: Session, recursos: list[RecursoRespuesta], usuarios: list[UsuarioRespuesta], hoy: date
) -> None:
    """Unas pocas reservas de un día de los días anteriores, para que «Pasadas» tenga contenido.

    Se insertan sin el servicio, que las rechazaría (regla 3), pero cumplen las demás: una por
    día, así no se solapan, y de trabajadores, porque un responsable no tiene reservas
    rechazadas y aprueba él mismo las suyas (regla 7).
    """
    trabajadores = [usuario for usuario in usuarios if usuario.rol == Rol.TRABAJADOR]
    responsable = next(usuario for usuario in usuarios if usuario.rol == Rol.RESPONSABLE)
    for indice in range(6):
        recurso = recursos[indice % len(recursos)]
        aprobada = indice % 2 == 0
        por_horas = recurso.modalidad_reserva in POR_HORAS
        session.add(
            Reserva(
                recurso_id=recurso.id,
                titular_id=trabajadores[indice % len(trabajadores)].id,
                aprobada_por_id=responsable.id if aprobada else None,
                fecha=hoy - timedelta(days=indice + 1),
                fecha_fin=hoy - timedelta(days=indice + 1),
                hora_inicio=time(10, 0) if por_horas else None,
                hora_fin=time(11, 0) if por_horas else None,
                asistentes_sala=2 if capacidad_compartida(recurso) is not None else None,
                estado=EstadoReserva.APROBADA if aprobada else EstadoReserva.RECHAZADA,
            )
        )


def main() -> None:
    print(f"Base de datos: {engine.url.render_as_string(hide_password=True)}")
    try:
        recrear_esquema(engine)
    except RuntimeError as error:
        sys.exit(str(error))

    with SessionLocal() as session:
        cargar_datos(session)
        session.commit()
        estados = generar_reservas(session, random.Random(2024))

    print(
        f"Datos de prueba cargados: 4 usuarios, 8 recursos y {estados.total()} reservas"
        f" ({estados[EstadoReserva.PENDIENTE]} pendientes, {estados[EstadoReserva.APROBADA]} aprobadas,"
        f" {estados[EstadoReserva.RECHAZADA]} rechazadas, {estados[EstadoReserva.CANCELADA]} canceladas)."
    )


if __name__ == "__main__":
    main()
