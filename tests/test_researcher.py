from nutricion.agents import researcher
from nutricion.agents.researcher import _GlossaryEntry, _PillDraft
from nutricion.domain.lesson import Pill
from nutricion.sources.feeds import Candidate


def cand(title: str) -> Candidate:
    return Candidate(title=title, url=f"https://x.com/{len(title)}", summary="", source="S")


def previous(angle: str) -> Pill:
    return Pill("Antes", "x", "y", "https://x.com/a", "¿?", angle=angle)


FUNDING = [cand("Startup raises $200M in Series B"), cand("Mistral valuation hits $14B")]
OTHERS = [
    cand("Hospital uses AI to cut wait times"),
    cand("EU finalizes AI Act rules"),
    cand("New coding tool for accountants"),
]


def test_funding_news_is_dropped_after_a_funding_pill():
    kept = researcher.diversify(FUNDING + OTHERS, [previous("inversión y financiación")])
    assert kept == OTHERS


def test_no_filter_when_too_few_alternatives_remain():
    pool = FUNDING + OTHERS[:1]
    assert researcher.diversify(pool, [previous("inversión y financiación")]) == pool


def test_no_filter_without_history():
    assert researcher.diversify(FUNDING, []) == FUNDING


def test_keyword_angle():
    assert researcher.keyword_angle(cand("OpenAI levanta una ronda")) == "inversión y financiación"
    assert researcher.keyword_angle(cand("EU AI Act enters into force")) == (
        "regulación y política"
    )
    assert researcher.keyword_angle(cand("Hospital uses AI")) == ""


class DraftLLM:
    def __init__(self, draft: _PillDraft) -> None:
        self.draft = draft

    def generate_structured(self, system, prompt, schema):
        self.prompt = prompt
        return self.draft


def draft(**overrides) -> _PillDraft:
    fields = dict(
        candidate_number=1,
        headline="H",
        what_happened="W",
        why_it_matters="M",
        challenge="C",
        options=["a", "b", "c"],
        key_figure="",
        key_figure_label="",
        angle="Caso de uso real",
        image_prompt="A hospital corridor",
        glossary=[
            _GlossaryEntry(term="LLM", definition="Large Language Model: IA que genera texto."),
            _GlossaryEntry(term=" ", definition="vacío"),
        ],
    )
    return _PillDraft(**{**fields, **overrides})


def test_glossary_and_angle_are_cleaned():
    pill, _ = researcher.create_pill(DraftLLM(draft()), OTHERS)
    assert pill.angle == "caso de uso real"
    assert pill.glossary == (("LLM", "Large Language Model: IA que genera texto."),)


def test_unknown_angle_is_discarded():
    pill, _ = researcher.create_pill(DraftLLM(draft(angle="otra cosa")), OTHERS)
    assert pill.angle == ""


def test_prompt_asks_for_glossary_and_lists_angles():
    llm = DraftLLM(draft())
    researcher.create_pill(llm, OTHERS, recent=[previous("caso de uso real")])
    assert "`glossary`" in llm.prompt and "«riesgos, seguridad y ética»" in llm.prompt
    assert llm.prompt.startswith("Píldoras anteriores")
