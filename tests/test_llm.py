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
