"""Nota de voz de la píldora (v4.2): guion hablado -> voz de Gemini -> MP3 para Telegram."""

import io
import re
import wave
from dataclasses import dataclass

import lameenc

from nutricion.domain.lesson import Pill
from nutricion.llm import LLMClient

BITRATE_KBPS = 48  # voz mono: suficiente y ligero (~6 KB por segundo)
_URL = re.compile(r"https?://\S+")


@dataclass(frozen=True)
class Voice:
    audio: bytes  # MP3
    duration: int  # segundos


def script(pill: Pill) -> str:
    """Guion hablado a partir de la píldora (sin llamada extra al LLM)."""
    parts = [
        f"Tu píldora de {pill.category.lower()}." if pill.category else "Tu píldora de hoy.",
        _sentence(pill.headline),
        pill.what_happened,
        f"¿Por qué importa? {pill.why_it_matters}",
        f"Y ahora, tu desafío: {pill.challenge}",
        "Elige una postura con los botones o respóndeme por escrito.",
    ]
    text = " ".join(_URL.sub("", p).strip() for p in parts if p and p.strip())
    return re.sub(r"\s+", " ", text)


def _sentence(text: str) -> str:
    text = text.strip()
    return text if not text or text[-1] in ".!?…" else f"{text}."


def to_mp3(wav_audio: bytes) -> Voice:
    """Convierte el WAV (PCM de 16 bits) que devuelve Gemini en MP3, que Telegram acepta
    como nota de voz."""
    with wave.open(io.BytesIO(wav_audio)) as w:
        channels, rate = w.getnchannels(), w.getframerate()
        frames = w.getnframes()
        pcm = w.readframes(frames)
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(BITRATE_KBPS)
    encoder.set_in_sample_rate(rate)
    encoder.set_channels(channels)
    encoder.set_quality(2)
    audio = bytes(encoder.encode(pcm) + encoder.flush())
    return Voice(audio=audio, duration=max(1, round(frames / rate)))


def build_voice(llm: LLMClient, pill: Pill) -> Voice:
    # Sin indicaciones de estilo: los modelos de voz las leerían en voz alta
    return to_mp3(llm.speak(script(pill)))
