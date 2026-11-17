"""Datos de prueba: borra y vuelve a crear las tablas (python -m app.seed)."""

import sys

from sqlalchemy.orm import Session

from app.common.enums import PoliticaCancelacion, Rol
from app.database import SessionLocal, engine, recrear_esquema
from app.entidades import Equipo, SalaReunion, Usuario, Vehiculo

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


def main() -> None:
    print(f"Base de datos: {engine.url.render_as_string(hide_password=True)}")
    try:
        recrear_esquema(engine)
    except RuntimeError as error:
        sys.exit(str(error))

    with SessionLocal() as session:
        cargar_datos(session)
        session.commit()
    print("Datos de prueba cargados: 4 usuarios y 8 recursos.")


if __name__ == "__main__":
    main()
