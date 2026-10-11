"""Servidor del webhook de Telegram: respuestas al instante a mensajes y botones.

Al arrancar registra su propia URL en Telegram (setWebhook). Responde 200 enseguida y procesa la
actualización en segundo plano, de una en una, para que Telegram no la reenvíe.
"""

import hmac
import json
import logging
import os
import threading
import time
import traceback
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

from nutricion.app import COMMANDS, OFFSET_KEY, REPORT_BUTTON
from nutricion.channels.telegram import TelegramClient
from nutricion.config import Settings, get_settings
from nutricion.factory import build_agent
from nutricion.memory.diagnose import connection_summary
from nutricion.memory.store import DatabaseConnectionError, Store

log = logging.getLogger("nutricion.web")


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


WEBHOOK_PATH = "/telegram"
_lock = threading.Lock()


# Si un mensaje anterior sigue procesándose más de este tiempo, se considera atascado
LOCK_TIMEOUT_S = 150
BUSY_KEY = "procesando"


def _warn(settings: Settings, text: str) -> None:
    try:
        TelegramClient(settings.telegram_bot_token).send_message(
            settings.telegram_chat_id, text, REPORT_BUTTON
        )
    except Exception:  # noqa: BLE001 - avisar es lo último que se intenta
        log.exception("No se pudo avisar por Telegram")


def _trace(agent, message: str) -> None:
    """Rastro de cada acción completada, para revisar qué pasó si algo no llega."""
    try:
        agent.store.log_event("traza", message)
    except Exception:  # noqa: BLE001
        log.exception("No se pudo registrar la traza")


def _describe(update: dict) -> str:
    if "callback_query" in update:
        return f"botón «{update['callback_query'].get('data', '')}»"
    text = ((update.get("message") or {}).get("text") or "").strip()
    return f"comando {text.split()[0]}" if text.startswith("/") else "mensaje de texto"


def _record_error(agent, what: str) -> None:
    try:
        agent.store.log_event("error", what, traceback.format_exc())
    except Exception:  # noqa: BLE001 - la base de datos puede ser la que falla
        log.exception("No se pudo registrar el error")


def _run_locked(settings: Settings, what: str, job, agent_factory) -> None:
    """Ejecuta un trabajo de uno en uno. Si otro sigue atascado, avisa en vez de esperar
    para siempre; los errores quedan registrados para /diagnostico y el usuario recibe aviso."""
    if not _lock.acquire(timeout=LOCK_TIMEOUT_S):
        log.error("Bloqueado: %s lleva más de %ss esperando", what, LOCK_TIMEOUT_S)
        _warn(
            settings,
            "⏳ Sigo ocupado con una tarea anterior que está tardando demasiado (quizá Gemini"
            " no responde). Vuelve a intentarlo en unos minutos.",
        )
        return
    try:
        try:
            agent = agent_factory(settings)
        except DatabaseConnectionError as exc:
            log.error("%s", exc)
            _warn(
                settings,
                "⚠️ El servidor no puede conectar con la base de datos. Revisa DATABASE_URL"
                " en Render.",
            )
            return
        started = time.monotonic()
        try:
            agent.store.set(BUSY_KEY, json.dumps({"tarea": what, "desde": _now()}))
            job(agent)
            _trace(agent, f"{what}: ok en {time.monotonic() - started:.1f} s")
        except Exception as exc:
            log.exception("Error en %s", what)
            _record_error(agent, f"{what}: {exc.__class__.__name__}: {str(exc)[:300]}")
            _warn(
                settings,
                "⚠️ Tuve un problema con tu última acción (quizá Gemini está saturado)."
                " Vuelve a intentarlo en unos minutos. Si se repite, pulsa «Reportar problema».",
            )
            raise
        finally:
            try:
                agent.store.set(BUSY_KEY, "")
                agent.store.close()
            except Exception:  # noqa: BLE001
                log.exception("No se pudo cerrar el almacén")
    finally:
        _lock.release()


def process(update: dict, settings: Settings, agent_factory=build_agent) -> None:
    what = f"{_describe(update)} (actualización {update.get('update_id')})"

    def job(agent):
        try:
            agent.handle_update(update)
        except Exception:
            # Telegram no la reenviará (ya respondimos 200): se da por procesada
            agent.store.set(OFFSET_KEY, str(update["update_id"] + 1))
            raise

    try:
        _run_locked(settings, what, job, agent_factory)
    except Exception:  # noqa: BLE001 - ya registrado y avisado
        pass


def run_daily_pill(settings: Settings, force: bool, agent_factory=build_agent) -> None:
    def job(agent):
        sent = agent.daily_pill_if_due(force=force)
        log.info("Píldora diaria %s", "enviada" if sent else "ya enviada hoy: se omite")

    try:
        _run_locked(settings, "píldora diaria", job, agent_factory)
    except Exception:  # noqa: BLE001 - ya registrado y avisado
        pass


def create_app(settings: Settings | None = None, agent_factory=build_agent) -> Starlette:
    settings = settings or get_settings()

    async def health(request: Request) -> PlainTextResponse:
        return PlainTextResponse("ok")

    def diagnostics() -> dict:
        """Estado de la configuración, sin revelar claves ni contraseñas."""
        events, busy = [], ""
        try:
            store = Store(settings.database)
            database = "ok" if settings.database_url else "SQLite local (falta DATABASE_URL)"
            events = store.recent_events(15)
            busy = store.get(BUSY_KEY) or ""
            store.close()
        except DatabaseConnectionError as exc:
            database = str(exc)
        return {
            # Commit desplegado (Render lo expone): confirma si un cambio ya está en producción
            "version": os.environ.get("RENDER_GIT_COMMIT", "")[:7] or "desconocida",
            "nota_de_voz": settings.voice_notes,
            "procesando_ahora": json.loads(busy) if busy else None,
            "eventos_recientes": events,
            "base_de_datos": database,
            "conexion": connection_summary(settings.database) if settings.database_url else None,
            "database_password": bool(settings.database_password),
            "gemini_api_key": bool(settings.gemini_api_key),
            "telegram_bot_token": bool(settings.telegram_bot_token),
            "telegram_chat_id": bool(settings.telegram_chat_id),
            "telegram_webhook_secret": bool(settings.telegram_webhook_secret),
            "cron_secret": bool(settings.cron_secret),
            "url_publica": settings.webhook_base_url or "no detectada",
        }

    def authorized(request: Request) -> bool:
        """Clave CRON_SECRET por parámetro ?clave= o cabecera X-Cron-Secret."""
        key = request.query_params.get("clave") or request.headers.get("x-cron-secret", "")
        return bool(settings.cron_secret) and hmac.compare_digest(key, settings.cron_secret)

    unauthorized = JSONResponse({"ok": False, "error": "clave incorrecta"}, status_code=401)

    async def cron_daily_pill(request: Request) -> JSONResponse:
        """Disparador de cron-job.org: responde al instante y envía la píldora en segundo plano."""
        if not authorized(request):
            return unauthorized
        force = request.query_params.get("forzar") == "1"
        task = BackgroundTask(run_daily_pill, settings, force, agent_factory)
        return JSONResponse({"ok": True, "pildora": "en preparación"}, background=task)

    async def diagnose(request: Request) -> JSONResponse:
        # Protegido: revela el destino de la base de datos (servidor, usuario del proyecto)
        if not authorized(request):
            return unauthorized
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
