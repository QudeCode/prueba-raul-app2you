from pydantic import BaseModel, ConfigDict

from app.common.enums import Rol


class UsuarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellidos: str
    rol: Rol
