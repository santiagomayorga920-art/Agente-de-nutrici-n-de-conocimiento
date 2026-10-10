"""Descarga de feeds en paralelo con tiempo límite y extracción de candidatas."""

import calendar
import html
import re
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import feedparser
import httpx

from nutricion.sources.catalog import SOURCES, Category, Source

PER_SOURCE = 5
# Algunos feeds (p. ej. OpenAI) devuelven todo su archivo: solo interesa lo reciente
MAX_AGE_DAYS = 7
_TAG = re.compile(r"<[^>]+>")
_IMG_SRC = re.compile(r"<img[^>]+src=[\"']([^\"']+)", re.IGNORECASE)
_USER_AGENT = "Mozilla/5.0 (compatible; nutricion-bot/0.1; +https://github.com)"


@dataclass(frozen=True)
class Candidate:
    title: str
    url: str
    summary: str
    source: str = ""
    category: Category = Category.NEGOCIOS
    image_url: str = ""


class NoNewsFound(Exception):
    pass


def fetch_source(source: Source, http: httpx.Client) -> list[Candidate]:
    response = http.get(source.url)
    response.raise_for_status()
    feed = feedparser.parse(response.content)
    candidates = []
    for entry in feed.entries:
        url = entry.get("link", "")
        if not url or _too_old(entry):
            continue
        raw_summary = entry.get("summary", "")
        candidates.append(
            Candidate(
                title=_clean(entry.get("title", "")),
                url=url,
                summary=_clean(raw_summary)[:400],
                source=_publisher(entry) or source.name,
                category=source.category,
                image_url=_entry_image(entry, raw_summary),
            )
        )
    return candidates


def fetch_candidates(seen_urls: set[str], sources: list[Source] = SOURCES) -> list[Candidate]:
    """Hasta PER_SOURCE noticias nuevas por fuente; una fuente caída no detiene a las demás."""
    with httpx.Client(
        timeout=15, follow_redirects=True, headers={"User-Agent": _USER_AGENT}
    ) as http:
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda s: _safe_fetch(s, http), sources))
    candidates = []
    for batch in results:
        fresh = [c for c in batch if c.url not in seen_urls]
        candidates.extend(fresh[:PER_SOURCE])
    if not candidates:
        raise NoNewsFound("Ninguna fuente devolvió noticias nuevas")
    return candidates


def source_health(sources: list[Source] = SOURCES) -> list[tuple[str, int | str]]:
    """Diagnóstico: cuántas entradas devuelve cada fuente (o el error)."""
    report: list[tuple[str, int | str]] = []
    with httpx.Client(
        timeout=15, follow_redirects=True, headers={"User-Agent": _USER_AGENT}
    ) as http:
        for source in sources:
            try:
                report.append((source.name, len(fetch_source(source, http))))
            except Exception as exc:  # noqa: BLE001 - es un informe, no se propaga
                report.append((source.name, f"error: {exc.__class__.__name__}"))
    return report


def _safe_fetch(source: Source, http: httpx.Client) -> list[Candidate]:
    try:
        return fetch_source(source, http)
    except Exception as exc:  # noqa: BLE001 - una fuente caída no debe tumbar el envío
        print(f"Fuente no disponible: {source.name} ({exc.__class__.__name__})")
        return []


def _too_old(entry, now: float | None = None) -> bool:
    published = entry.get("published_parsed") or entry.get("updated_parsed")
    if not published:
        return False  # sin fecha: se deja pasar y decide el LLM
    age_days = ((now or time.time()) - calendar.timegm(published)) / 86_400
    return age_days > MAX_AGE_DAYS


def normalize_title(title: str) -> str:
    """Clave para detectar la misma noticia en varias fuentes (quita el " - Medio" final)."""
    title = re.sub(r"\s+[-–|]\s+[^-–|]{2,40}$", "", title)
    return " ".join(re.sub(r"[^\w\s]", " ", title.lower()).split())


def _clean(text: str) -> str:
    return " ".join(html.unescape(_TAG.sub(" ", text)).split())


def _publisher(entry) -> str:
    # Google News indica el medio original en <source>
    source = entry.get("source")
    return source.get("title", "") if isinstance(source, dict) else ""


def _entry_image(entry, raw_summary: str) -> str:
    for key in ("media_content", "media_thumbnail"):
        for media in entry.get(key) or []:
            if media.get("url"):
                return media["url"]
    for link in entry.get("links") or []:
        if link.get("type", "").startswith("image/") and link.get("href"):
            return link["href"]
    match = _IMG_SRC.search(raw_summary)
    return match.group(1) if match else ""
