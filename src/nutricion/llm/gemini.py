"""Implementación de LLMClient con la capa gratuita de Gemini (Google AI Studio)."""

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
    def __init__(self, api_key: str, model: str, fallback_model: str = "") -> None:
        self._client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=TIMEOUT_MS, retry_options=types.HttpRetryOptions(attempts=2)
            ),
        )
        self._models = [m for m in (model, fallback_model) if m]

    def generate(self, system: str, prompt: str) -> str:
        return self._call(prompt, types.GenerateContentConfig(system_instruction=system))

    def generate_structured(self, system: str, prompt: str, schema: type[T]) -> T:
        config = types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json",
            response_schema=schema,
        )
        return schema.model_validate_json(self._call(prompt, config))

    def _call(self, prompt: str, config: types.GenerateContentConfig) -> str:
        for i, model in enumerate(self._models):
            try:
                response = self._client.models.generate_content(
                    model=model, contents=prompt, config=config
                )
                return response.text or ""
            except errors.APIError as exc:
                if exc.code not in _RETRYABLE or i == len(self._models) - 1:
                    raise
            except httpx.TimeoutException:
                if i == len(self._models) - 1:
                    raise
        raise AssertionError("inalcanzable")
