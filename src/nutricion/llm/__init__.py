"""Cerebro del agente tras una interfaz común: se cambia de proveedor sin tocar el resto."""

from typing import Protocol, TypeVar

from pydantic import BaseModel

from nutricion.config import Settings

T = TypeVar("T", bound=BaseModel)


class LLMClient(Protocol):
    def generate(self, system: str, prompt: str) -> str:
        """Devuelve texto libre."""
        ...

    def generate_structured(self, system: str, prompt: str, schema: type[T]) -> T:
        """Devuelve una instancia de `schema` validada (p. ej. la nota de una evaluación)."""
        ...

    def speak(self, text: str) -> bytes:
        """Lee el texto en voz alta y devuelve el audio en WAV (PCM de 16 bits)."""
        ...


class MissingAPIKey(Exception):
    pass


def get_llm(settings: Settings) -> LLMClient:
    if not settings.gemini_api_key:
        raise MissingAPIKey("Falta GEMINI_API_KEY")
    from nutricion.llm.gemini import GeminiClient

    return GeminiClient(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        fallback_model=settings.gemini_fallback_model,
        tts_models=(settings.gemini_tts_model, settings.gemini_tts_fallback_model),
        voice=settings.gemini_tts_voice,
    )
