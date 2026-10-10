"""Máquina de estados de la lección: píldora -> desafío -> espera -> feedback -> completada."""

from dataclasses import dataclass
from enum import StrEnum


class LessonState(StrEnum):
    PENDING = "pending"  # píldora generada, aún no enviada
    AWAITING_ANSWER = "awaiting_answer"  # píldora y desafío enviados; esperando respuesta
    EVALUATING = "evaluating"  # respuesta recibida; el tutor la está evaluando
    COMPLETED = "completed"  # feedback enviado; se puede pasar a la siguiente


_TRANSITIONS: dict[LessonState, set[LessonState]] = {
    LessonState.PENDING: {LessonState.AWAITING_ANSWER},
    LessonState.AWAITING_ANSWER: {LessonState.EVALUATING},
    # Si la evaluación falla (error de API), se vuelve a esperar sin perder la respuesta
    LessonState.EVALUATING: {LessonState.COMPLETED, LessonState.AWAITING_ANSWER},
    LessonState.COMPLETED: set(),
}


class InvalidTransition(Exception):
    pass


def transition(current: LessonState, target: LessonState) -> LessonState:
    if target not in _TRANSITIONS[current]:
        raise InvalidTransition(f"{current} -> {target} no está permitido")
    return target


@dataclass(frozen=True)
class Pill:
    headline: str
    what_happened: str
    why_it_matters: str
    source_url: str
    challenge: str
    source_name: str = ""
    category: str = ""
    image_url: str = ""
    # Posturas de respuesta rápida que se muestran como botones
    options: tuple[str, ...] = ()


@dataclass(frozen=True)
class Lesson:
    id: int
    pill: Pill
    state: LessonState
    choice: str = ""  # opción elegida con un botón, si la hubo
