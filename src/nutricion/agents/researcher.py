"""Investigador: lee feeds RSS gratuitos y convierte la noticia más relevante en una píldora."""

from dataclasses import dataclass

import feedparser
from pydantic import BaseModel

from nutricion.agents.skills import load_skill
from nutricion.domain.lesson import Pill
from nutricion.llm import LLMClient

FEEDS = [
    "https://news.google.com/rss/search?q=inteligencia+artificial+negocios+OR+inversi%C3%B3n+when:2d"
    "&hl=es-419&gl=US&ceid=US:es-419",
    "https://news.google.com/rss/search?q=artificial+intelligence+business+OR+funding+when:2d"
    "&hl=en-US&gl=US&ceid=US:en",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
]


@dataclass(frozen=True)
class Candidate:
    title: str
    url: str
    summary: str


class NoNewsFound(Exception):
    pass


def fetch_candidates(seen_urls: set[str], limit: int = 30) -> list[Candidate]:
    candidates: list[Candidate] = []
    for feed_url in FEEDS:
        for entry in feedparser.parse(feed_url).entries:
            url = entry.get("link", "")
            if url and url not in seen_urls:
                summary = entry.get("summary", "")[:500]
                candidates.append(Candidate(entry.get("title", ""), url, summary))
    if not candidates:
        raise NoNewsFound("Ningún feed devolvió noticias nuevas")
    return candidates[:limit]


class _PillDraft(BaseModel):
    candidate_number: int
    headline: str
    what_happened: str
    why_it_matters: str
    challenge: str


def create_pill(llm: LLMClient, candidates: list[Candidate]) -> Pill:
    system = load_skill("researching-ai") + "\n\n" + load_skill("evaluating-user")
    listing = "\n\n".join(
        f"[{i}] {c.title}\n{c.summary}\n{c.url}" for i, c in enumerate(candidates, start=1)
    )
    prompt = (
        "Estas son las noticias candidatas de hoy. Elige UNA sola, la más relevante según tus"
        " criterios, indica su número en candidate_number, escribe la píldora en español y"
        " formula el desafío.\n\n" + listing
    )
    draft = llm.generate_structured(system, prompt, _PillDraft)
    index = min(max(draft.candidate_number, 1), len(candidates)) - 1
    return Pill(
        headline=draft.headline,
        what_happened=draft.what_happened,
        why_it_matters=draft.why_it_matters,
        source_url=candidates[index].url,
        challenge=draft.challenge,
    )
