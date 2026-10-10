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
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

from nutricion.app import COMMANDS, OFFSET_KEY, Agent
from nutricion.channels.telegram import TelegramClient
from nutricion.config import Settings, get_settings
from nutricion.llm import get_llm
from nutricion.memory.store import Store

log = logging.getLogger("nutricion.web")
WEBHOOK_PATH = "/telegram"
_lock = threading.Lock()


def build_agent(settings: Settings) -> Agent:
    return Agent(
        store=Store(settings.database),
        llm=get_llm(settings),
        messenger=TelegramClient(settings.telegram_bot_token),
        chat_id=settings.telegram_chat_id,
        timezone=settings.timezone,
    )


def process(update: dict, settings: Settings, agent_factory=build_agent) -> None:
    with _lock:
        agent = agent_factory(settings)
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


def create_app(settings: Settings | None = None, agent_factory=build_agent) -> Starlette:
    settings = settings or get_settings()

    async def health(request: Request) -> PlainTextResponse:
        return PlainTextResponse("ok")

    async def telegram(request: Request) -> JSONResponse:
        secret = request.headers.get("x-telegram-bot-api-secret-token", "")
        if not settings.telegram_webhook_secret or not hmac.compare_digest(
            secret, settings.telegram_webhook_secret
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
            client.set_webhook(base + WEBHOOK_PATH, settings.telegram_webhook_secret)
            client.set_commands(COMMANDS)
            log.info("Webhook registrado en %s", base + WEBHOOK_PATH)
        yield

    routes = [Route("/", health), Route(WEBHOOK_PATH, telegram, methods=["POST"])]
    return Starlette(routes=routes, lifespan=lifespan)


def __getattr__(name: str):
    # `uvicorn nutricion.web:app` crea la app con la configuración del entorno
    if name == "app":
        logging.basicConfig(level=logging.INFO)
        return create_app()
    raise AttributeError(name)
