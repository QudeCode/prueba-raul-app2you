from sqlalchemy.orm import Mapped, mapped_column

from app.common.enums import Rol
from app.database import Base, check_enum, tipo_enum


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (check_enum("rol", Rol, "ck_usuario_rol"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str]
    apellidos: Mapped[str]
    rol: Mapped[Rol] = mapped_column(tipo_enum(Rol))
