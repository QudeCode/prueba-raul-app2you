from typing import Annotated

from fastapi import Depends

from app.usuarios.dto import UsuarioRespuesta
from app.usuarios.repository import UsuarioRepository, get_usuario_repository


class UsuarioService:
    def __init__(self, repositorio: UsuarioRepository):
        self.repositorio = repositorio

    def listar(self) -> list[UsuarioRespuesta]:
        return [UsuarioRespuesta.model_validate(usuario) for usuario in self.repositorio.listar()]


def get_usuario_service(
    repositorio: Annotated[UsuarioRepository, Depends(get_usuario_repository)],
) -> UsuarioService:
    return UsuarioService(repositorio)
