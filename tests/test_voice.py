import io
import wave

from nutricion.domain.lesson import Pill
from nutricion.llm.gemini import as_wav
from nutricion.media import voice


def pill(**overrides) -> Pill:
    fields = dict(
        headline="OpenAI levanta 200 M USD",
        what_happened="Anunció una ronda. Más detalles en https://example.com/nota",
        why_it_matters="Cambia la competencia.",
        source_url="https://example.com/nota",
        challenge="¿Invertirías?",
        category="Negocios",
    )
    return Pill(**{**fields, **overrides})


def wav(seconds: float, rate: int = 24_000) -> bytes:
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * int(seconds * rate))
    return out.getvalue()


def test_script_reads_the_pill_without_urls():
    text = voice.script(pill())
    assert text.startswith("Tu píldora de negocios. OpenAI levanta 200 M USD. Anunció")
    assert "¿Por qué importa? Cambia la competencia." in text
    assert "tu desafío: ¿Invertirías?" in text
    assert "http" not in text and "  " not in text


def test_script_without_category():
    assert voice.script(pill(category="")).startswith("Tu píldora de hoy.")


def test_wav_is_encoded_as_mp3_with_duration():
    result = voice.to_mp3(wav(3.2))
    assert result.duration == 3
    assert result.audio[:3] == b"ID3" or result.audio[0] == 0xFF  # cabecera MP3
    assert len(result.audio) < 30_000


def test_raw_pcm_from_gemini_is_wrapped_as_wav():
    pcm = b"\x01\x00" * 16_000
    data = as_wav(pcm, "audio/L16;codec=pcm;rate=16000")
    with wave.open(io.BytesIO(data)) as w:
        assert w.getframerate() == 16_000 and w.getnframes() == 16_000
    assert as_wav(data, "audio/wav") == data


class FakeSpeaker:
    def speak(self, text):
        self.text = text
        return wav(1.0)


def test_build_voice_sends_only_the_script_to_the_model():
    speaker = FakeSpeaker()
    result = voice.build_voice(speaker, pill())
    assert speaker.text == voice.script(pill())
    assert result.duration == 1
