"""Configuración central cargada desde variables de entorno o un archivo .env."""

import hashlib
import os
import re
from functools import lru_cache
from urllib.parse import quote

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
    # Opcional: la contraseña aparte. Así se puede pegar la URI de Supabase tal cual, con
    # [YOUR-PASSWORD], y el código inserta la contraseña (codificada si tiene símbolos)
    database_password: str = ""
    database_path: str = "data/nutricion.db"
    # Modo webhook (tiempo real): secreto que Telegram envía en cada petición
    telegram_webhook_secret: str = ""
    # Clave que cron-job.org envía para disparar la píldora diaria (solo letras y números)
    cron_secret: str = ""
    # URL pública del servidor; en Render se toma sola de RENDER_EXTERNAL_URL
    public_url: str = ""
    # Zona horaria para calcular la racha de días (p. ej. America/Bogota, America/Mexico_City)
    timezone: str = "UTC"

    @property
    def database(self) -> str:
        url = self.database_url.strip()
        if not url:
            return f"sqlite:///{self.database_path}"
        if self.database_password:
            password = quote(self.database_password.strip(), safe="")
            url = re.sub(r"\[YOUR-PASSWORD\]", password, url, flags=re.IGNORECASE)
        return url

    @property
    def telegram_secret_token(self) -> str:
        """Versión del secreto apta para Telegram, que solo admite [A-Za-z0-9_-] (Render lo
        genera en base64, con + / =). Se usa igual al registrar el webhook y al validarlo."""
        if not self.telegram_webhook_secret:
            return ""
        return hashlib.sha256(self.telegram_webhook_secret.encode()).hexdigest()

    @property
    def webhook_base_url(self) -> str:
        return (self.public_url or os.environ.get("RENDER_EXTERNAL_URL", "")).rstrip("/")


@lru_cache
def get_settings() -> Settings:
    return Settings()
