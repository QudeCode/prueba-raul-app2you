from collections.abc import Iterator
from enum import StrEnum

from sqlalchemy import CheckConstraint, Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_session() -> Iterator[Session]:
    """Sesión por petición. Nunca hace commit: al cerrarse deshace lo no confirmado (decisión 0002)."""
    with SessionLocal() as session:
        yield session


def check_enum(columna: str, enum: type[StrEnum], nombre: str) -> CheckConstraint:
    """CHECK que limita la columna a los valores del enum (decisión 0004)."""
    valores = ", ".join(f"'{miembro.value}'" for miembro in enum)
    return CheckConstraint(f"{columna} IN ({valores})", name=nombre)


def recrear_esquema(engine: Engine) -> None:
    """Borra y vuelve a crear todas las tablas (decisión 0003)."""
    import app.entidades  # noqa: F401  registra las entidades en Base.metadata

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
