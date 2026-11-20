from typing import Annotated

from fastapi import APIRouter, Depends

from app.recursos.dto import RecursoRespuesta
from app.recursos.service import RecursoService, get_recurso_service

router = APIRouter(prefix="/recursos", tags=["recursos"])


@router.get("")
def listar(service: Annotated[RecursoService, Depends(get_recurso_service)]) -> list[RecursoRespuesta]:
    return service.listar()
