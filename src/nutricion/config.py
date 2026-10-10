"""Configuración central cargada desde variables de entorno o un archivo .env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    database_url: str = "sqlite:///nutricion.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
