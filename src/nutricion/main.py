"""Punto de entrada de la aplicación."""

from nutricion import __version__
from nutricion.config import get_settings


def main() -> None:
    settings = get_settings()
    missing = [
        name
        for name in ("anthropic_api_key", "telegram_bot_token", "telegram_chat_id")
        if not getattr(settings, name)
    ]
    print(f"nutricion v{__version__} · modelo: {settings.claude_model}")
    if missing:
        print("Faltan variables en .env: " + ", ".join(n.upper() for n in missing))
    else:
        print("Configuración completa.")


if __name__ == "__main__":
    main()
