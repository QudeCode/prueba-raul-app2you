from typing import Annotated

from fastapi import Depends

from app.common.errores import ErrorDominio, NoAutenticado, NoEncontrado
from app.usuarios.dto import UsuarioRespuesta
from app.usuarios.repository import UsuarioRepository, get_usuario_repository


class UsuarioService:
    def __init__(self, repositorio: UsuarioRepository):
        self.repositorio = repositorio

    def listar(self) -> list[UsuarioRespuesta]:
        return [UsuarioRespuesta.model_validate(usuario) for usuario in self.repositorio.listar()]

    def obtener(self, usuario_id: int) -> UsuarioRespuesta:
        return self._buscar(usuario_id, NoEncontrado(f"No existe el usuario {usuario_id}"))

    def obtener_actual(self, usuario_id: int) -> UsuarioRespuesta:
        """El usuario de la cabecera X-Usuario-Id; si no existe es un 401, no un 404 (decisión 0011)."""
        return self._buscar(usuario_id, NoAutenticado(f"Usuario desconocido: {usuario_id}"))

    def _buscar(self, usuario_id: int, si_no_existe: ErrorDominio) -> UsuarioRespuesta:
        usuario = self.repositorio.obtener(usuario_id)
        if usuario is None:
            raise si_no_existe
        return UsuarioRespuesta.model_validate(usuario)


def get_usuario_service(
    repositorio: Annotated[UsuarioRepository, Depends(get_usuario_repository)],
) -> UsuarioService:
    return UsuarioService(repositorio)
