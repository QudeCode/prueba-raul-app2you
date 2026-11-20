from typing import Annotated

from fastapi import APIRouter, Depends, Header

from app.usuarios.dto import UsuarioRespuesta
from app.usuarios.service import UsuarioService, get_usuario_service

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def get_usuario_actual(
    x_usuario_id: Annotated[int, Header(alias="X-Usuario-Id")],
    service: Annotated[UsuarioService, Depends(get_usuario_service)],
) -> UsuarioRespuesta:
    """Usuario actual sin login: lo identifica la cabecera X-Usuario-Id (decisión 0011)."""
    return service.obtener_actual(x_usuario_id)


UsuarioActual = Annotated[UsuarioRespuesta, Depends(get_usuario_actual)]


@router.get("")
def listar(service: Annotated[UsuarioService, Depends(get_usuario_service)]) -> list[UsuarioRespuesta]:
    return service.listar()
