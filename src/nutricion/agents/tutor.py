"""Tutor: reacciona a la postura elegida con un botón y evalúa la respuesta escrita."""

from pydantic import BaseModel

from nutricion.agents.skills import load_skill
from nutricion.domain.lesson import Pill
from nutricion.domain.progress import Score
from nutricion.llm import LLMClient


class Evaluation(BaseModel):
    comprension: int
    razonamiento: int
    perspectiva_negocio: int
    feedback: str

    def score(self) -> Score:
        """Notas acotadas a 1–5 aunque el LLM devuelva valores fuera de rango."""
        return Score(self.comprension, self.razonamiento, self.perspectiva_negocio)


def react_to_choice(llm: LLMClient, pill: Pill, choice: str) -> str:
    prompt = (
        f"Noticia: {pill.headline}\nDesafío: {pill.challenge}\n\n"
        f"El usuario eligió rápidamente esta postura: «{choice}».\n\n"
        "Reacciona en 2–3 frases en español: señala una consecuencia o un riesgo concreto de esa"
        " postura que quizá no esté considerando, y termina pidiéndole que justifique su elección"
        " por escrito. No evalúes todavía ni pongas nota."
    )
    return llm.generate(load_skill("evaluating-user"), prompt)


def evaluate(llm: LLMClient, pill: Pill, answer: str, choice: str = "") -> Evaluation:
    chosen = f"Postura elegida con botón: «{choice}»\n\n" if choice else ""
    prompt = (
        f"Noticia: {pill.headline}\n{pill.what_happened}\n\n"
        f"Desafío planteado: {pill.challenge}\n\n"
        f"{chosen}Respuesta del usuario:\n{answer}\n\n"
        "Puntúa cada criterio de 1 a 5 y escribe el feedback en español."
    )
    return llm.generate_structured(load_skill("evaluating-user"), prompt, Evaluation)
