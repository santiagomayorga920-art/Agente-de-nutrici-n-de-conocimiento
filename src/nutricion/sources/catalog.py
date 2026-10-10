"""Catálogo de fuentes. Todas son gratuitas, sin clave y de uso permitido (RSS públicos o API)."""

from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import urlencode


class Category(StrEnum):
    NEGOCIOS = "Negocios"
    FINANZAS = "Finanzas"
    INVESTIGACION = "Investigación"


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    category: Category


def _google_news(query: str, lang: str = "es-419", country: str = "US") -> str:
    ceid = f"{country}:{lang}"
    return "https://news.google.com/rss/search?" + urlencode(
        {"q": f"{query} when:2d", "hl": lang, "gl": country, "ceid": ceid}
    )


_ARXIV_QUERY = (
    "(cat:cs.AI OR cat:cs.LG OR cat:econ.GN OR cat:q-fin.GN) AND "
    "(abs:business OR abs:economic OR abs:market OR abs:finance OR abs:enterprise OR abs:labor)"
)

SOURCES: list[Source] = [
    # Negocios: prensa generalista y anuncios de los grandes laboratorios
    Source(
        "Google News (ES)",
        _google_news("inteligencia artificial empresas OR inversión"),
        Category.NEGOCIOS,
    ),
    Source(
        "Google News (EN)",
        _google_news("artificial intelligence business OR startup OR funding", "en-US"),
        Category.NEGOCIOS,
    ),
    Source(
        "TechCrunch AI",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        Category.NEGOCIOS,
    ),
    Source("OpenAI News", "https://openai.com/news/rss.xml", Category.NEGOCIOS),
    Source("Google DeepMind", "https://deepmind.google/blog/rss.xml", Category.NEGOCIOS),
    # Finanzas: Bloomberg no tiene API gratuita y su web prohíbe el scraping, así que se usan sus
    # titulares indexados por Google News (legal) más el RSS público de CNBC
    Source(
        "Bloomberg (vía Google News)",
        _google_news("artificial intelligence site:bloomberg.com", "en-US"),
        Category.FINANZAS,
    ),
    Source(
        "Financial Times (vía Google News)",
        _google_news("artificial intelligence site:ft.com", "en-US"),
        Category.FINANZAS,
    ),
    Source("CNBC Tech", "https://www.cnbc.com/id/19854910/device/rss/rss.html", Category.FINANZAS),
    # Investigación: papers y universidades
    Source(
        "arXiv",
        "https://export.arxiv.org/api/query?"
        + urlencode(
            {
                "search_query": _ARXIV_QUERY,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "max_results": 15,
            }
        ),
        Category.INVESTIGACION,
    ),
    Source(
        "MIT News (IA)",
        "https://news.mit.edu/rss/topic/artificial-intelligence2",
        Category.INVESTIGACION,
    ),
    Source(
        "Berkeley AI Research", "https://bair.berkeley.edu/blog/feed.xml", Category.INVESTIGACION
    ),
]


def category_of_the_day(lessons_so_far: int) -> Category:
    """Rota la categoría preferida para que las píldoras no sean siempre del mismo tipo."""
    categories = list(Category)
    return categories[lessons_so_far % len(categories)]
