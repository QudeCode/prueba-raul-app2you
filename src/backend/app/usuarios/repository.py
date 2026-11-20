from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.usuarios.entity import Usuario


class UsuarioRepository:
    def __init__(self, session: Session):
        self.session = session

    def listar(self) -> list[Usuario]:
        consulta = select(Usuario).order_by(Usuario.apellidos, Usuario.nombre, Usuario.id)
        return list(self.session.scalars(consulta))


def get_usuario_repository(session: Annotated[Session, Depends(get_session)]) -> UsuarioRepository:
    return UsuarioRepository(session)
