"""Punto de entrada de la aplicación."""

import sys

from nutricion import __version__
from nutricion.config import get_settings
from nutricion.llm import get_llm


def main() -> None:
    settings = get_settings()
    missing = [
        name
        for name in ("gemini_api_key", "telegram_bot_token", "telegram_chat_id")
        if not getattr(settings, name)
    ]
    print(f"nutricion v{__version__} · modelo: {settings.gemini_model}")
    if missing:
        print("Faltan variables en .env: " + ", ".join(n.upper() for n in missing))

    if "--ping" in sys.argv and settings.gemini_api_key:
        reply = get_llm(settings).generate("Responde en una sola palabra.", "Di 'hola' en español.")
        print(f"Gemini responde: {reply.strip()}")


if __name__ == "__main__":
    main()
