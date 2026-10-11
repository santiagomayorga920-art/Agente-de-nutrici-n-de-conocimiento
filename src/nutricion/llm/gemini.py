"""Implementación de LLMClient con la capa gratuita de Gemini (Google AI Studio)."""

import io
import re
import time
import wave
from typing import TypeVar

import httpx
from google import genai
from google.genai import errors, types
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

# Saturación (503), tiempo agotado en Google (504) o cuota agotada (429): merece la pena probar
# con el modelo de respaldo
_RETRYABLE = {429, 500, 502, 503, 504}
# Límite por petición: sin él una llamada colgada bloquearía el bot indefinidamente
TIMEOUT_MS = 60_000
# Reintentos automáticos solo ante fallos pasajeros; con cuota agotada (429) reintentar el mismo
# modelo solo hace esperar: se pasa directo al de respaldo
# (tampoco 504: el modelo ya tardó todo su plazo y reintentarlo duplica la espera)
_HTTP_RETRY = types.HttpRetryOptions(attempts=2, http_status_codes=[408, 500, 502, 503])
# Tiempo que se omite un modelo sin cuota si Google no indica cuándo se recupera
DEFAULT_SKIP_S = 600
MAX_SKIP_S = 24 * 3600
# Modelo -> momento (time.monotonic) hasta el que se omite por cuota agotada. Es global porque
# el servidor crea un cliente por mensaje y la cuota es de la clave, no del cliente
_exhausted: dict[str, float] = {}


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
            http_options=types.HttpOptions(timeout=TIMEOUT_MS, retry_options=_HTTP_RETRY),
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
        now = time.monotonic()
        # Los modelos sin cuota van al final (no se descartan: puede que ya se haya recuperado)
        models = sorted(models, key=lambda m: _exhausted.get(m, 0) > now)
        for i, model in enumerate(models):
            try:
                response = self._client.models.generate_content(
                    model=model, contents=prompt, config=config
                )
                _exhausted.pop(model, None)
                return response
            except errors.APIError as exc:
                if exc.code == 429:
                    _exhausted[model] = time.monotonic() + retry_delay(exc)
                if exc.code not in _RETRYABLE or i == len(models) - 1:
                    raise
            except httpx.TimeoutException:
                if i == len(models) - 1:
                    raise
        raise AssertionError("inalcanzable")


def retry_delay(exc: errors.APIError) -> float:
    """Segundos hasta que Google vuelve a dar cuota (p. ej. «retryDelay: 83071s»)."""
    match = re.search(r"retryDelay['\"]?\s*:\s*['\"](\d+(?:\.\d+)?)s", str(exc))
    return min(float(match.group(1)), MAX_SKIP_S) if match else DEFAULT_SKIP_S


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
