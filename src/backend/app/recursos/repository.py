from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.enums import TipoRecurso
from app.database import get_session
from app.recursos.entity import Recurso


class RecursoRepository:
    def __init__(self, session: Session):
        self.session = session

    def listar(self, tipo: TipoRecurso | None = None) -> list[Recurso]:
        """Devuelve cada recurso como su subclase (SalaReunion, Vehiculo o Equipo)."""
        consulta = select(Recurso).order_by(Recurso.nombre, Recurso.id)
        if tipo is not None:
            consulta = consulta.where(Recurso.tipo == tipo)
        return list(self.session.scalars(consulta))


def get_recurso_repository(session: Annotated[Session, Depends(get_session)]) -> RecursoRepository:
    return RecursoRepository(session)
