"""Construcción del agente con sus dependencias reales (sin depender del servidor web)."""

from nutricion.app import Agent
from nutricion.channels.telegram import TelegramClient
from nutricion.config import Settings
from nutricion.llm import get_llm
from nutricion.memory.store import Store


def build_agent(settings: Settings, store: Store | None = None) -> Agent:
    return Agent(
        store=store or Store(settings.database),
        llm=get_llm(settings),
        messenger=TelegramClient(settings.telegram_bot_token),
        chat_id=settings.telegram_chat_id,
        timezone=settings.timezone,
    )
