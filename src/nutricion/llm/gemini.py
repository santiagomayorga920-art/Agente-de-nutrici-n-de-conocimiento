"""Implementación de LLMClient con la capa gratuita de Gemini (Google AI Studio)."""

import io
import re
import wave
from typing import TypeVar

import httpx
from google import genai
from google.genai import errors, types
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

# Saturación (503) o cuota agotada (429): merece la pena probar con el modelo de respaldo
_RETRYABLE = {429, 500, 503}
# Límite por petición: sin él una llamada colgada bloquearía el bot indefinidamente
TIMEOUT_MS = 60_000


class GeminiClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        fallback_model: str = "",
        tts_models: tuple[str, ...] = (),
        voice: str = "Sulafat",
    ) -> None:
        self._client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=TIMEOUT_MS, retry_options=types.HttpRetryOptions(attempts=2)
            ),
        )
        self._models = [m for m in (model, fallback_model) if m]
        self._tts_models = [m for m in tts_models if m]
        self._voice = voice

    def generate(self, system: str, prompt: str) -> str:
        return self._call(prompt, types.GenerateContentConfig(system_instruction=system))

    def generate_structured(self, system: str, prompt: str, schema: type[T]) -> T:
        config = types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json",
            response_schema=schema,
        )
        return schema.model_validate_json(self._call(prompt, config))

    def speak(self, text: str) -> bytes:
        config = types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=self._voice)
                )
            ),
        )
        response = self._generate(self._tts_models, text, config)
        blob = response.candidates[0].content.parts[0].inline_data
        return as_wav(blob.data, blob.mime_type or "")

    def _call(self, prompt: str, config: types.GenerateContentConfig) -> str:
        return self._generate(self._models, prompt, config).text or ""

    def _generate(
        self, models: list[str], prompt: str, config: types.GenerateContentConfig
    ) -> types.GenerateContentResponse:
        if not models:
            raise ValueError("No hay modelo configurado")
        for i, model in enumerate(models):
            try:
                return self._client.models.generate_content(
                    model=model, contents=prompt, config=config
                )
            except errors.APIError as exc:
                if exc.code not in _RETRYABLE or i == len(models) - 1:
                    raise
            except httpx.TimeoutException:
                if i == len(models) - 1:
                    raise
        raise AssertionError("inalcanzable")


def as_wav(data: bytes, mime_type: str) -> bytes:
    """Los modelos de voz devuelven WAV o PCM crudo («audio/L16;rate=24000»): se unifica a WAV."""
    if data[:4] == b"RIFF":
        return data
    match = re.search(r"rate=(\d+)", mime_type)
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(int(match.group(1)) if match else 24_000)
        w.writeframes(data)
    return out.getvalue()
