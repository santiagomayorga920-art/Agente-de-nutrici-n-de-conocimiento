"""Punto de entrada: `nutricion [revisar|ping|fuentes|stats|migrar|tick [--enviar-pildora]]`."""

import argparse
import os
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
    sub.add_parser("fuentes", help="diagnóstico: cuántas noticias devuelve cada fuente")
    sub.add_parser("stats", help="muestra tu perfil en la terminal")
    sub.add_parser("webhook", help="estado del webhook según Telegram (sin mostrar el token)")
    migrate = sub.add_parser("migrar", help="copia una base SQLite a la base configurada")
    migrate.add_argument("origen", help="ruta del archivo SQLite de origen")
    tick = sub.add_parser("tick", help="procesa mensajes de Telegram y envía la píldora si toca")
    tick.add_argument("--enviar-pildora", action="store_true", help="enviar la píldora diaria")
    args = parser.parse_args()

    settings = get_settings()
    if args.command == "ping":
        reply = get_llm(settings).generate("Responde en una sola palabra.", "Di 'hola' en español.")
        print(f"Gemini responde: {reply.strip()}")
    elif args.command == "fuentes":
        from nutricion.sources.feeds import source_health

        for name, result in source_health():
            print(f"{name:<36} {result}")
    elif args.command == "stats":
        _print_stats(settings)
    elif args.command == "webhook":
        _print_webhook(settings)
    elif args.command == "migrar":
        _migrate(settings, args.origen)
    elif args.command == "tick":
        _require(settings)
        _run_tick(settings, args.enviar_pildora)
    else:
        print(f"nutricion v{__version__} · modelo: {settings.gemini_model}")
        print(f"Base de datos: {_database_status(settings)}")
        missing = [n.upper() for n in REQUIRED if not getattr(settings, n)]
        print("Faltan variables: " + ", ".join(missing) if missing else "Configuración completa.")


def _database_status(settings: Settings) -> str:
    from nutricion.memory.store import DatabaseConnectionError, Store

    if not settings.database_url:
        return "SQLite (local)"
    try:
        Store(settings.database).close()
        return "Postgres (conexión correcta)"
    except DatabaseConnectionError as exc:
        return f"Postgres con ERROR\n{exc}"


def _require(settings: Settings) -> None:
    missing = [n.upper() for n in REQUIRED if not getattr(settings, n)]
    if missing:
        sys.exit("Faltan variables: " + ", ".join(missing))


def annotate(level: str, title: str, message: str) -> None:
    """Muestra el mensaje en la terminal y como aviso en la página de la ejecución de GitHub."""
    print(message)
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::{level} title={title}::" + message.replace("\n", "%0A"))


def open_store(settings: Settings):
    """La base configurada; si Postgres falla, SQLite local para que el bot no se detenga."""
    from nutricion.memory.store import DatabaseConnectionError, Store

    try:
        return Store(settings.database)
    except DatabaseConnectionError as exc:
        if not settings.database_url:
            raise
        annotate(
            "warning",
            "Supabase no disponible: usando SQLite",
            f"{exc}\nEl bot sigue funcionando con la base SQLite de la caché de Actions.",
        )
        return Store(f"sqlite:///{settings.database_path}")


def _run_tick(settings: Settings, send_daily_pill: bool) -> None:
    from nutricion.channels.telegram import TelegramClient
    from nutricion.factory import build_agent

    # Con un webhook activo Telegram no permite getUpdates: el servidor ya atiende los mensajes
    webhook = TelegramClient(settings.telegram_bot_token).webhook_url()
    agent = build_agent(settings, open_store(settings))
    try:
        agent.tick(send_daily_pill, poll=not webhook)
    finally:
        agent.store.close()
    mode = "webhook activo, solo píldora diaria" if webhook else "sondeo"
    print(f"Tick completado ({mode}).")


def _print_webhook(settings: Settings) -> None:
    from datetime import UTC, datetime

    from nutricion.channels.telegram import TelegramClient

    info = TelegramClient(settings.telegram_bot_token).webhook_info()
    print(f"URL registrada: {info.get('url') or '(ninguna: el bot funciona por sondeo)'}")
    print(f"Mensajes pendientes de entregar: {info.get('pending_update_count', 0)}")
    if info.get("last_error_date"):
        when = datetime.fromtimestamp(info["last_error_date"], UTC).strftime("%Y-%m-%d %H:%M UTC")
        print(f"Último error de entrega ({when}): {info.get('last_error_message')}")
    else:
        print("Último error de entrega: ninguno")


def _print_stats(settings: Settings) -> None:
    import re

    from nutricion.channels.formatting import profile_card
    from nutricion.domain.progress import build_profile
    from nutricion.memory.store import Store

    store = Store(settings.database)
    card = profile_card(build_profile(store.scores(), tz=settings.timezone))
    print(re.sub(r"</?[bi]>", "", card))
    store.close()


def _migrate(settings: Settings, source: str) -> None:
    from pathlib import Path

    from nutricion.memory.store import DatabaseConnectionError, Store

    if not settings.database_url:
        sys.exit("DATABASE_URL no está definida: no hay a dónde migrar.")
    if not Path(source).exists():
        print(f"No existe {source}: nada que migrar.")
        return
    try:
        target = Store(settings.database)
    except DatabaseConnectionError as exc:
        annotate("error", "Revisa el Secret DATABASE_URL", str(exc))
        sys.exit(1)
    origin = Store(f"sqlite:///{source}")
    if target.get("migrado_desde_sqlite"):
        print("La migración ya se hizo antes.")
    else:
        copied = target.import_from(origin)
        target.set("migrado_desde_sqlite", "1")
        print(f"Migradas {copied} lecciones.")
    origin.close()
    target.close()


if __name__ == "__main__":
    main()
