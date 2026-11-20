from datetime import time
from typing import Annotated

from pydantic import AfterValidator, PlainSerializer

# Día reservable por horas: la hora de fin máxima es 23:59 (regla 2, decisión 0013)
INICIO_DIA = time(0, 0)
FIN_DIA = time(23, 59)


def _sin_segundos(hora: time) -> time:
    if hora.second or hora.microsecond or hora.tzinfo is not None:
        raise ValueError("La hora va en minutos, sin segundos (HH:MM)")
    return hora


def formato_hora(hora: time) -> str:
    return hora.strftime("%H:%M")


# Hora en minutos (regla 2): rechaza segundos y zona horaria, y se serializa como "HH:MM"
HoraMinuto = Annotated[
    time, AfterValidator(_sin_segundos), PlainSerializer(formato_hora, return_type=str)
]
