"""Punto de entrada: `nutricion [revisar|ping|tick [--enviar-pildora]]`."""

import argparse
import sys

from nutricion import __version__
from nutricion.config import Settings, get_settings
from nutricion.llm import get_llm

REQUIRED = ("gemini_api_key", "telegram_bot_token", "telegram_chat_id")


def main() -> None:
    parser = argparse.ArgumentParser(prog="nutricion")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("revisar", help="comprueba la configuración (por defecto)")
    sub.add_parser("ping", help="prueba real contra Gemini")
    tick = sub.add_parser("tick", help="procesa mensajes de Telegram y envía la píldora si toca")
    tick.add_argument("--enviar-pildora", action="store_true", help="enviar la píldora diaria")
    args = parser.parse_args()

    settings = get_settings()
    if args.command == "ping":
        reply = get_llm(settings).generate("Responde en una sola palabra.", "Di 'hola' en español.")
        print(f"Gemini responde: {reply.strip()}")
    elif args.command == "tick":
        _require(settings)
        _run_tick(settings, args.enviar_pildora)
    else:
        print(f"nutricion v{__version__} · modelo: {settings.gemini_model}")
        missing = [n.upper() for n in REQUIRED if not getattr(settings, n)]
        print("Faltan variables: " + ", ".join(missing) if missing else "Configuración completa.")


def _require(settings: Settings) -> None:
    missing = [n.upper() for n in REQUIRED if not getattr(settings, n)]
    if missing:
        sys.exit("Faltan variables: " + ", ".join(missing))


def _run_tick(settings: Settings, send_daily_pill: bool) -> None:
    from nutricion.app import Agent
    from nutricion.channels.telegram import TelegramClient
    from nutricion.memory.store import Store

    agent = Agent(
        store=Store(settings.database_path),
        llm=get_llm(settings),
        messenger=TelegramClient(settings.telegram_bot_token),
        chat_id=settings.telegram_chat_id,
    )
    agent.tick(send_daily_pill)
    print("Tick completado.")


if __name__ == "__main__":
    main()
