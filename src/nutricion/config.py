"""Configuración central cargada desde variables de entorno o un archivo .env."""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gemini_api_key: str = ""
    gemini_model: str = "gemini-flash-latest"
    gemini_fallback_model: str = "gemini-flash-lite-latest"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    # Postgres (Supabase) si está definida; si no, SQLite en database_path
    database_url: str = ""
    database_path: str = "data/nutricion.db"
    # Modo webhook (tiempo real): secreto que Telegram envía en cada petición
    telegram_webhook_secret: str = ""
    # URL pública del servidor; en Render se toma sola de RENDER_EXTERNAL_URL
    public_url: str = ""
    # Zona horaria para calcular la racha de días (p. ej. America/Bogota, America/Mexico_City)
    timezone: str = "UTC"

    @property
    def database(self) -> str:
        return self.database_url or f"sqlite:///{self.database_path}"

    @property
    def webhook_base_url(self) -> str:
        return (self.public_url or os.environ.get("RENDER_EXTERNAL_URL", "")).rstrip("/")


@lru_cache
def get_settings() -> Settings:
    return Settings()
