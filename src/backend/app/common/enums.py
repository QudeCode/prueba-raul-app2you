from enum import StrEnum

# El valor de cada miembro es igual a su nombre (decisión 0004)


class Rol(StrEnum):
    TRABAJADOR = "TRABAJADOR"
    RESPONSABLE = "RESPONSABLE"


class TipoRecurso(StrEnum):
    SALA_REUNION = "SALA_REUNION"
    VEHICULO = "VEHICULO"
    EQUIPO = "EQUIPO"


class PoliticaCancelacion(StrEnum):
    FLEXIBLE = "FLEXIBLE"
    MODERADA = "MODERADA"
    BLOQUEADA = "BLOQUEADA"


class ModalidadReserva(StrEnum):
    POR_HORAS = "POR_HORAS"
    DIA_COMPLETO = "DIA_COMPLETO"
    AMBAS = "AMBAS"


class EstadoReserva(StrEnum):
    PENDIENTE = "PENDIENTE"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"
    CANCELADA = "CANCELADA"
