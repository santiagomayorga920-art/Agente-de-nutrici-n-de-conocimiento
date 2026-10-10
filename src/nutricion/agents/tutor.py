"""Tutor: evalúa la respuesta del usuario al desafío según la rúbrica de evaluating-user."""

from pydantic import BaseModel

from nutricion.agents.skills import load_skill
from nutricion.domain.lesson import Pill
from nutricion.llm import LLMClient


class Evaluation(BaseModel):
    comprension: int
    razonamiento: int
    perspectiva_negocio: int
    feedback: str

    def scores_line(self) -> str:
        def clamp(n: int) -> int:
            return min(max(n, 1), 5)

        return (
            f"Comprensión {clamp(self.comprension)}/5 · "
            f"Razonamiento {clamp(self.razonamiento)}/5 · "
            f"Negocio {clamp(self.perspectiva_negocio)}/5"
        )


def evaluate(llm: LLMClient, pill: Pill, answer: str) -> Evaluation:
    prompt = (
        f"Noticia: {pill.headline}\n{pill.what_happened}\n\n"
        f"Desafío planteado: {pill.challenge}\n\n"
        f"Respuesta del usuario:\n{answer}\n\n"
        "Puntúa cada criterio de 1 a 5 y escribe el feedback en español."
    )
    return llm.generate_structured(load_skill("evaluating-user"), prompt, Evaluation)
