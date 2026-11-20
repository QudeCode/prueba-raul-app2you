from typing import Annotated

from fastapi import APIRouter, Depends

from app.usuarios.dto import UsuarioRespuesta
from app.usuarios.service import UsuarioService, get_usuario_service

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("")
def listar(service: Annotated[UsuarioService, Depends(get_usuario_service)]) -> list[UsuarioRespuesta]:
    return service.listar()
