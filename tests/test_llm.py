import time

import pytest

from nutricion.config import Settings
from nutricion.llm import MissingAPIKey, get_llm
from nutricion.llm.gemini import GeminiClient


def test_missing_key_is_reported():
    with pytest.raises(MissingAPIKey):
        get_llm(Settings(_env_file=None, gemini_api_key=""))


def test_gemini_is_selected_when_key_present():
    llm = get_llm(Settings(_env_file=None, gemini_api_key="clave-de-prueba"))
    assert isinstance(llm, GeminiClient)


class _Models:
    def __init__(self, fail: set[str]) -> None:
        self.fail = fail
        self.calls: list[str] = []

    def generate_content(self, model, contents, config):
        from google.genai import errors

        self.calls.append(model)
        if model in self.fail:
            body = {"error": {"message": "cuota", "details": [{"retryDelay": "83071s"}]}}
            raise errors.ClientError(429, body)

        class Response:
            text = "ok"

        return Response()


def test_exhausted_model_is_skipped_until_quota_returns(monkeypatch):
    from nutricion.llm import gemini

    monkeypatch.setattr(gemini, "_exhausted", {})
    llm = GeminiClient(api_key="x", model="principal", fallback_model="respaldo")
    models = _Models(fail={"principal"})
    llm._client = type("C", (), {"models": models})()
    assert llm.generate("s", "p") == "ok"
    assert llm.generate("s", "p") == "ok"
    # La segunda vez va directo al respaldo, sin perder tiempo con el modelo sin cuota
    assert models.calls == ["principal", "respaldo", "respaldo"]
    assert 80_000 < gemini._exhausted["principal"] - time.monotonic() < 84_000
