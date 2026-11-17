from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# src/backend/.env, sea cual sea el directorio desde el que se arranca
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    database_url: str


# Sin DATABASE_URL la aplicación no arranca (ValidationError al importar)
settings = Settings()
