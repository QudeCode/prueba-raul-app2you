from typing import Annotated

from fastapi import APIRouter, Depends

from app.common.enums import TipoRecurso
from app.recursos.dto import RecursoRespuesta
from app.recursos.service import RecursoService, get_recurso_service

router = APIRouter(prefix="/recursos", tags=["recursos"])


@router.get("")
def listar(
    service: Annotated[RecursoService, Depends(get_recurso_service)],
    tipo: TipoRecurso | None = None,
) -> list[RecursoRespuesta]:
    return service.listar(tipo)


@router.get("/{recurso_id}")
def obtener(
    service: Annotated[RecursoService, Depends(get_recurso_service)], recurso_id: int
) -> RecursoRespuesta:
    return service.obtener(recurso_id)
