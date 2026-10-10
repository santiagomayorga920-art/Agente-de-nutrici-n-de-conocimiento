"""Investigador: elige la noticia más relevante entre todas las fuentes y escribe la píldora."""

from pydantic import BaseModel

from nutricion.agents.skills import load_skill
from nutricion.domain.lesson import Pill
from nutricion.llm import LLMClient
from nutricion.sources.catalog import Category
from nutricion.sources.feeds import Candidate

MAX_OPTIONS = 4
MAX_OPTION_LEN = 40


class _PillDraft(BaseModel):
    candidate_number: int
    headline: str
    what_happened: str
    why_it_matters: str
    challenge: str
    options: list[str]


def create_pill(
    llm: LLMClient, candidates: list[Candidate], preferred: Category | None = None
) -> Pill:
    system = load_skill("researching-ai") + "\n\n" + load_skill("evaluating-user")
    listing = "\n\n".join(
        f"[{i}] ({c.category} · {c.source}) {c.title}\n{c.summary}"
        for i, c in enumerate(candidates, start=1)
    )
    preference = (
        f"Hoy prioriza la categoría «{preferred}» si hay una candidata sólida; si no, elige la"
        " mejor de cualquier categoría.\n"
        if preferred
        else ""
    )
    prompt = (
        "Estas son las noticias candidatas. Elige UNA sola según tus criterios de rigor y"
        " relevancia e indica su número en candidate_number. "
        + preference
        + "Escribe la píldora en español, formula el desafío y propón en `options` de 3 a 4"
        f" posturas de respuesta rápida (máximo {MAX_OPTION_LEN} caracteres cada una).\n\n"
        + listing
    )
    draft = llm.generate_structured(system, prompt, _PillDraft)
    chosen = candidates[min(max(draft.candidate_number, 1), len(candidates)) - 1]
    options = tuple(o.strip()[:MAX_OPTION_LEN] for o in draft.options if o.strip())
    return Pill(
        headline=draft.headline,
        what_happened=draft.what_happened,
        why_it_matters=draft.why_it_matters,
        source_url=chosen.url,
        challenge=draft.challenge,
        source_name=chosen.source,
        category=chosen.category,
        image_url=chosen.image_url,
        options=options[:MAX_OPTIONS],
    )
