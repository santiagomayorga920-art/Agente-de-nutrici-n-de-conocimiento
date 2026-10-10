"""Carga las instrucciones de `skills/<nombre>/SKILL.md` para usarlas como prompt de sistema."""

from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[3] / "skills"


def load_skill(name: str) -> str:
    text = (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    return text.strip()
