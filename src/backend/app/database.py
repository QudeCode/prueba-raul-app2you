from collections.abc import Iterator
from enum import StrEnum

from sqlalchemy import URL, CheckConstraint, Engine, Enum, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)

# None es un socket Unix; host.docker.internal, la máquina local vista desde el devcontainer
HOSTS_LOCALES = {None, "localhost", "127.0.0.1", "::1", "host.docker.internal"}


class Base(DeclarativeBase):
    pass


def get_session() -> Iterator[Session]:
    """Sesión por petición. Nunca hace commit: al cerrarse deshace lo no confirmado (decisión 0002)."""
    with SessionLocal() as session:
        yield session


def tipo_enum(enum: type[StrEnum]) -> Enum:
    """Columna VARCHAR que se lee como el enum, sin tipo nativo ni CHECK automático (decisión 0004)."""
    return Enum(
        enum,
        native_enum=False,
        create_constraint=False,
        length=None,
        values_callable=lambda miembros: [miembro.value for miembro in miembros],
    )


def check_enum(columna: str, enum: type[StrEnum], nombre: str) -> CheckConstraint:
    """CHECK que limita la columna a los valores del enum (decisión 0004)."""
    valores = ", ".join(f"'{miembro.value}'" for miembro in enum)
    return CheckConstraint(f"{columna} IN ({valores})", name=nombre)


def es_local(url: URL) -> bool:
    host = url.host.lower() if url.host else None
    return host in HOSTS_LOCALES


def recrear_esquema(engine: Engine) -> None:
    """Borra y vuelve a crear todas las tablas, solo en una base local (decisión 0007)."""
    if not es_local(engine.url):
        raise RuntimeError(f"Solo se recrea el esquema de una base local (host: {engine.url.host})")

    import app.entidades  # noqa: F401  registra las entidades en Base.metadata

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
