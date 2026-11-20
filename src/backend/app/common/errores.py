"""Errores del dominio: los servicios los lanzan sin saber nada de HTTP (decisión 0012)."""


class ErrorDominio(Exception):
    """Base de los errores del dominio; el mensaje, en español, es str(error)."""


class NoEncontrado(ErrorDominio):
    """El recurso, la reserva o el usuario pedido no existe."""


class NoAutenticado(ErrorDominio):
    """El usuario actual (X-Usuario-Id) no existe."""


class NoPermitido(ErrorDominio):
    """Quien llama no tiene el rol o no es el titular (reglas 9 y 13)."""


class ReglaIncumplida(ErrorDominio):
    """La petición incumple una regla por sí sola (reglas 2, 3, 4 y 18)."""


class Conflicto(ErrorDominio):
    """La petición choca con el estado actual: solapes, aforo, estado de la reserva o plazos."""
