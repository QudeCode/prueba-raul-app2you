"""Importa todas las entidades para que sus tablas queden registradas en Base.metadata."""

from app.recursos.entity import Equipo, Recurso, SalaReunion, Vehiculo
from app.reservas.entity import Reserva
from app.usuarios.entity import Usuario

__all__ = ["Equipo", "Recurso", "Reserva", "SalaReunion", "Usuario", "Vehiculo"]
