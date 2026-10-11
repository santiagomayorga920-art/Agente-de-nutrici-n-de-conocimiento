"""Construcción del agente con sus dependencias reales (sin depender del servidor web)."""

from nutricion.app import Agent
from nutricion.channels.telegram import TelegramClient
from nutricion.config import Settings
from nutricion.llm import get_llm
from nutricion.media import illustration, voice
from nutricion.memory.store import Store


def build_agent(settings: Settings, store: Store | None = None) -> Agent:
    llm = get_llm(settings)
    return Agent(
        store=store or Store(settings.database),
        llm=llm,
        messenger=TelegramClient(settings.telegram_bot_token),
        chat_id=settings.telegram_chat_id,
        timezone=settings.timezone,
        make_voice=(lambda pill: voice.build_voice(llm, pill)) if settings.voice_notes else None,
        make_illustration=(
            (
                lambda pill: illustration.generate(
                    illustration.prompt_for(pill),
                    settings.cloudflare_account_id,
                    settings.cloudflare_api_token,
                )
            )
            if settings.illustrations
            else None
        ),
    )
