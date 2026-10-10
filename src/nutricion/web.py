"""Servidor del webhook de Telegram: respuestas al instante a mensajes y botones.

Al arrancar registra su propia URL en Telegram (setWebhook). Responde 200 enseguida y procesa la
actualización en segundo plano, de una en una, para que Telegram no la reenvíe.
"""

import hmac
import logging
import threading
from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

from nutricion.app import COMMANDS, OFFSET_KEY
from nutricion.channels.telegram import TelegramClient
from nutricion.config import Settings, get_settings
from nutricion.factory import build_agent
from nutricion.memory.store import DatabaseConnectionError, Store

log = logging.getLogger("nutricion.web")
WEBHOOK_PATH = "/telegram"
_lock = threading.Lock()


def process(update: dict, settings: Settings, agent_factory=build_agent) -> None:
    with _lock:
        try:
            agent = agent_factory(settings)
        except DatabaseConnectionError as exc:
            log.error("%s", exc)
            TelegramClient(settings.telegram_bot_token).send_message(
                settings.telegram_chat_id,
                "⚠️ El servidor no puede conectar con la base de datos. Revisa DATABASE_URL en"
                " Render (abre /diagnostico en la URL del servidor para ver el motivo).",
            )
            return
        try:
            agent.handle_update(update)
        except Exception:
            log.exception("Error procesando la actualización %s", update.get("update_id"))
            # Telegram no la reenviará (ya respondimos 200): se avisa y se da por procesada
            agent.store.set(OFFSET_KEY, str(update["update_id"] + 1))
            agent.messenger.send_message(
                settings.telegram_chat_id,
                "⚠️ Tuve un problema procesando tu mensaje (quizá Gemini está saturado)."
                " Vuelve a enviarlo en unos minutos.",
            )
        finally:
            agent.store.close()


def run_daily_pill(settings: Settings, force: bool, agent_factory=build_agent) -> None:
    with _lock:
        agent = agent_factory(settings)
        try:
            sent = agent.daily_pill_if_due(force=force)
            log.info("Píldora diaria %s", "enviada" if sent else "ya enviada hoy: se omite")
        except Exception:
            log.exception("Error enviando la píldora diaria")
        finally:
            agent.store.close()


def create_app(settings: Settings | None = None, agent_factory=build_agent) -> Starlette:
    settings = settings or get_settings()

    async def health(request: Request) -> PlainTextResponse:
        return PlainTextResponse("ok")

    def diagnostics() -> dict:
        """Estado de la configuración, sin revelar claves ni contraseñas."""
        try:
            Store(settings.database).close()
            database = "ok" if settings.database_url else "SQLite local (falta DATABASE_URL)"
        except DatabaseConnectionError as exc:
            database = str(exc)
        return {
            "base_de_datos": database,
            "gemini_api_key": bool(settings.gemini_api_key),
            "telegram_bot_token": bool(settings.telegram_bot_token),
            "telegram_chat_id": bool(settings.telegram_chat_id),
            "telegram_webhook_secret": bool(settings.telegram_webhook_secret),
            "cron_secret": bool(settings.cron_secret),
            "url_publica": settings.webhook_base_url or "no detectada",
        }

    async def cron_daily_pill(request: Request) -> JSONResponse:
        """Disparador de cron-job.org: responde al instante y envía la píldora en segundo plano."""
        key = request.query_params.get("clave") or request.headers.get("x-cron-secret", "")
        if not settings.cron_secret or not hmac.compare_digest(key, settings.cron_secret):
            return JSONResponse({"ok": False, "error": "clave incorrecta"}, status_code=401)
        force = request.query_params.get("forzar") == "1"
        task = BackgroundTask(run_daily_pill, settings, force, agent_factory)
        return JSONResponse({"ok": True, "pildora": "en preparación"}, background=task)

    async def diagnose(request: Request) -> JSONResponse:
        return JSONResponse(await run_in_threadpool(diagnostics))

    async def telegram(request: Request) -> JSONResponse:
        secret = request.headers.get("x-telegram-bot-api-secret-token", "")
        if not settings.telegram_secret_token or not hmac.compare_digest(
            secret, settings.telegram_secret_token
        ):
            return JSONResponse({"ok": False}, status_code=401)
        update = await request.json()
        task = BackgroundTask(process, update, settings, agent_factory)
        return JSONResponse({"ok": True}, background=task)

    @asynccontextmanager
    async def lifespan(app: Starlette):
        base = settings.webhook_base_url
        if base and settings.telegram_bot_token and settings.telegram_webhook_secret:
            client = TelegramClient(settings.telegram_bot_token)
            try:
                client.set_webhook(base + WEBHOOK_PATH, settings.telegram_secret_token)
                client.set_commands(COMMANDS)
                log.info("Webhook registrado en %s", base + WEBHOOK_PATH)
            except Exception:
                # Un token incorrecto no debe impedir que arranque /diagnostico
                log.exception("No se pudo registrar el webhook en Telegram")
        yield

    routes = [
        Route("/", health),
        Route("/diagnostico", diagnose),
        Route("/cron/pildora", cron_daily_pill, methods=["GET", "POST"]),
        Route(WEBHOOK_PATH, telegram, methods=["POST"]),
    ]
    return Starlette(routes=routes, lifespan=lifespan)


def __getattr__(name: str):
    # `uvicorn nutricion.web:app` crea la app con la configuración del entorno
    if name == "app":
        logging.basicConfig(level=logging.INFO)
        return create_app()
    raise AttributeError(name)
