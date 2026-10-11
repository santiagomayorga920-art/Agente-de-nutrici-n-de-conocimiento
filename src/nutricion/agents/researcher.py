"""Investigador: elige la noticia más relevante entre todas las fuentes y escribe la píldora."""

import re

from pydantic import BaseModel

from nutricion.agents.skills import load_skill
from nutricion.domain.lesson import Pill
from nutricion.llm import LLMClient
from nutricion.sources.catalog import Category
from nutricion.sources.feeds import Candidate

MAX_OPTIONS = 4
MAX_OPTION_LEN = 40
MAX_FIGURE_LEN = 14
MAX_LABEL_LEN = 60
MAX_GLOSSARY = 4
MAX_TERM_LEN = 40
MAX_DEFINITION_LEN = 140
MAX_IMAGE_PROMPT_LEN = 400
# Cuántas píldoras anteriores se muestran al LLM para que no repita tema ni enfoque
HISTORY = 5
# Mínimo de candidatas que deben quedar tras descartar las del mismo ángulo que la anterior
MIN_CANDIDATES = 3

# Ángulos temáticos: cada píldora declara el suyo y la siguiente debe cambiarlo
ANGLES = (
    "inversión y financiación",
    "caso de uso real",
    "regulación y política",
    "herramienta o producto aplicado",
    "análisis de mercado y competencia",
    "investigación y avance técnico",
    "infraestructura y costos",
    "trabajo y talento",
    "riesgos, seguridad y ética",
)
# Palabras que delatan el ángulo de una noticia antes de pasarla al LLM (solo los evidentes)
_ANGLE_KEYWORDS = {
    "inversión y financiación": re.compile(
        r"\b(raises?|raised|funding|series [a-e]\b|valuation|valued at|invests?|investment|"
        r"ronda|financiaci[oó]n|valoraci[oó]n|levanta|recauda|invierte|inversi[oó]n|"
        r"unicornio|unicorn)",
        re.IGNORECASE,
    ),
    "regulación y política": re.compile(
        r"\b(regulat\w*|lawsuit|antitrust|ai act|legislat\w*|regulaci[oó]n|ley |"
        r"demanda|antimonopolio|senado|congress)",
        re.IGNORECASE,
    ),
}


def _shorten(text: str, limit: int) -> str:
    """Recorta en un límite de palabra (nunca a mitad de palabra)."""
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",;:-") + "…"


class _GlossaryEntry(BaseModel):
    term: str
    definition: str


class _PillDraft(BaseModel):
    candidate_number: int
    headline: str
    what_happened: str
    why_it_matters: str
    challenge: str
    options: list[str]
    key_figure: str
    key_figure_label: str
    angle: str
    glossary: list[_GlossaryEntry]
    image_prompt: str


def keyword_angle(candidate: Candidate) -> str:
    """Ángulo evidente por palabras clave del titular (o "" si no es obvio)."""
    for angle, pattern in _ANGLE_KEYWORDS.items():
        if pattern.search(candidate.title):
            return angle
    return ""


def diversify(candidates: list[Candidate], recent: list[Pill]) -> list[Candidate]:
    """Descarta las candidatas con el mismo ángulo que la píldora anterior, si quedan
    suficientes alternativas (si no, el LLM decide con el historial a la vista)."""
    if not recent or not recent[0].angle:
        return candidates
    varied = [c for c in candidates if keyword_angle(c) != recent[0].angle]
    return varied if len(varied) >= MIN_CANDIDATES else candidates


def _history(recent: list[Pill]) -> str:
    if not recent:
        return ""
    lines = "\n".join(
        f"- {'(' + p.angle + ') ' if p.angle else ''}{p.headline}" for p in recent[:HISTORY]
    )
    return (
        "Píldoras anteriores (de la más reciente a la más antigua):\n"
        f"{lines}\n"
        "VARIEDAD OBLIGATORIA: no repitas el ángulo de la píldora más reciente y evita los de"
        " las dos anteriores si hay una candidata sólida de otro ángulo. Penaliza también"
        " repetir la misma empresa protagonista o la misma tesis («X invierte millones en Y»)."
        " Ante dos candidatas de calidad parecida, elige la del ángulo menos visto.\n\n"
    )


def create_pill(
    llm: LLMClient,
    candidates: list[Candidate],
    preferred: Category | None = None,
    recent: list[Pill] | None = None,
) -> tuple[Pill, Candidate]:
    """Devuelve la píldora y la candidata original elegida (para marcarla como leída)."""
    recent = recent or []
    candidates = diversify(candidates, recent)
    system = load_skill("researching-ai") + "\n\n" + load_skill("evaluating-user")
    listing = "\n\n".join(
        f"[{i}] ({c.category} · {c.source}) {c.title}\n{c.summary}"
        for i, c in enumerate(candidates, start=1)
    )
    angles = ", ".join(f"«{a}»" for a in ANGLES)
    preference = (
        f"Hoy prioriza la categoría «{preferred}» si hay una candidata sólida; si no, elige la"
        " mejor de cualquier categoría.\n"
        if preferred
        else ""
    )
    prompt = (
        _history(recent)
        + "Estas son las noticias candidatas. Elige UNA sola según tus criterios de rigor,"
        " relevancia y variedad e indica su número en candidate_number. "
        + preference
        + "Escribe la píldora en español, formula el desafío y propón en `options` de 3 a 4"
        f" posturas de respuesta rápida (máximo {MAX_OPTION_LEN} caracteres cada una)."
        " Para la tarjeta visual, extrae en `key_figure` la cifra más llamativa de la noticia,"
        " corta (máximo 14 caracteres, p. ej. «200 M USD», «-35 %», «3x»), en notación"
        " española: millones = «M» y miles de millones = «mil M» (p. ej. «100 mil M USD»);"
        " nunca «B», «bn» ni «billones». En"
        " `key_figure_label` qué representa (máximo 50 caracteres). Si no hay una cifra clara,"
        " deja ambos vacíos; no inventes números."
        f" En `angle` indica el ángulo de la noticia elegida, exactamente uno de: {angles}."
        f" En `glossary` incluye de 1 a {MAX_GLOSSARY} términos técnicos, acrónimos o jerga de"
        " IA o negocios que aparezcan en tu píldora (p. ej. LLM, GPU, inferencia, ARR,"
        " Serie B), cada uno con una explicación de máximo 15 palabras para alguien sin"
        " formación técnica; si es un acrónimo, empieza por su significado. Lista vacía solo"
        " si la píldora no tiene ninguna jerga."
        " En `image_prompt` describe EN INGLÉS, en máximo 40 palabras, una escena para la"
        " ilustración de fondo: una metáfora visual concreta de la noticia (objetos, lugar,"
        " acción). Sin texto, letras, cifras, logotipos ni rostros de personas reales.\n\n"
        + listing
    )
    draft = llm.generate_structured(system, prompt, _PillDraft)
    angle = draft.angle.strip().lower()
    glossary = tuple(
        (_shorten(e.term, MAX_TERM_LEN), _shorten(e.definition, MAX_DEFINITION_LEN))
        for e in draft.glossary
        if e.term.strip() and e.definition.strip()
    )
    chosen = candidates[min(max(draft.candidate_number, 1), len(candidates)) - 1]
    options = tuple(o.strip()[:MAX_OPTION_LEN] for o in draft.options if o.strip())
    pill = Pill(
        headline=draft.headline,
        what_happened=draft.what_happened,
        why_it_matters=draft.why_it_matters,
        source_url=chosen.url,
        challenge=draft.challenge,
        source_name=chosen.source,
        category=chosen.category,
        image_url=chosen.image_url,
        options=options[:MAX_OPTIONS],
        key_figure=draft.key_figure.strip()[:MAX_FIGURE_LEN],
        key_figure_label=_shorten(draft.key_figure_label, MAX_LABEL_LEN),
        angle=angle if angle in ANGLES else "",
        glossary=glossary[:MAX_GLOSSARY],
        image_prompt=_shorten(draft.image_prompt, MAX_IMAGE_PROMPT_LEN),
    )
    return pill, chosen
