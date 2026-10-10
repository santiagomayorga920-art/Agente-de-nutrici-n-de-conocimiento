"""Orquestador: una ejecución ("tick") procesa tus mensajes pendientes y, si toca, envía la píldora.

Está pensado para correr de forma programada (GitHub Actions): no se queda esperando. Telegram
guarda tus mensajes hasta 24 h y el siguiente tick los recoge.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from nutricion.agents import researcher, tutor
from nutricion.domain.lesson import Lesson, LessonState, Pill
from nutricion.llm import LLMClient
from nutricion.memory.store import Store

OFFSET_KEY = "telegram_offset"
# EVALUATING también admite respuesta: un tick anterior pudo fallar a mitad de la evaluación
_ANSWERABLE = (LessonState.AWAITING_ANSWER, LessonState.EVALUATING)

WELCOME = (
    "¡Hola! Soy tu agente de nutrición de conocimiento. Cada día te enviaré una píldora sobre IA"
    " y negocios con un desafío. Respóndelo aquí cuando quieras y te daré feedback.\n\n"
    "Comandos: /siguiente para pedir una nueva píldora."
)
NO_PENDING = (
    "No tienes ningún desafío pendiente. Escribe /siguiente para recibir una nueva píldora."
)


class Messenger(Protocol):
    def get_updates(self, offset: int) -> list[dict]: ...

    def send_message(self, chat_id: str, text: str) -> None: ...


@dataclass
class Agent:
    store: Store
    llm: LLMClient
    messenger: Messenger
    chat_id: str
    fetch_candidates: Callable[[set[str]], list[researcher.Candidate]] = researcher.fetch_candidates

    def tick(self, send_daily_pill: bool) -> None:
        self.process_messages()
        if send_daily_pill:
            self.daily_pill()

    def process_messages(self) -> None:
        offset = int(self.store.get(OFFSET_KEY) or 0)
        for update in self.messenger.get_updates(offset):
            message = update.get("message") or {}
            text = (message.get("text") or "").strip()
            if str(message.get("chat", {}).get("id")) == self.chat_id and text:
                self._handle(text)
            # Se avanza tras procesar: si algo falla, el mensaje se reintenta en el próximo tick
            self.store.set(OFFSET_KEY, str(update["update_id"] + 1))

    def daily_pill(self) -> None:
        lesson = self.store.open_lesson()
        if lesson and lesson.state is LessonState.AWAITING_ANSWER:
            self._send(f"⏳ Aún tienes pendiente este desafío:\n\n{_format_pill(lesson.pill)}")
        else:
            self._deliver_new_pill()

    def _handle(self, text: str) -> None:
        command = text.split()[0].lower()
        lesson = self.store.open_lesson()
        if command == "/start":
            self._send(WELCOME)
        elif command == "/siguiente":
            if lesson and lesson.state is LessonState.AWAITING_ANSWER:
                self._send("Primero responde el desafío pendiente 🙂\n\n" + lesson.pill.challenge)
            else:
                self._deliver_new_pill()
        elif lesson and lesson.state in _ANSWERABLE:
            self._evaluate(lesson, text)
        else:
            self._send(NO_PENDING)

    def _deliver_new_pill(self) -> None:
        lesson = self.store.open_lesson()
        if not (lesson and lesson.state is LessonState.PENDING):
            # Si un envío anterior falló, se reutiliza esa píldora en vez de generar otra
            candidates = self.fetch_candidates(self.store.seen_urls())
            lesson = self.store.add_lesson(researcher.create_pill(self.llm, candidates))
        self._send(_format_pill(lesson.pill))
        self.store.move(lesson, LessonState.AWAITING_ANSWER)

    def _evaluate(self, lesson: Lesson, answer: str) -> None:
        self.store.save_answer(lesson, answer)
        if lesson.state is LessonState.AWAITING_ANSWER:
            lesson = self.store.move(lesson, LessonState.EVALUATING)
        try:
            evaluation = tutor.evaluate(self.llm, lesson.pill, answer)
        except Exception:
            self.store.move(lesson, LessonState.AWAITING_ANSWER)
            raise
        self.store.save_feedback(lesson, evaluation.feedback, evaluation.scores_line())
        self._send(
            f"📊 {evaluation.scores_line()}\n\n{evaluation.feedback}\n\n"
            "✅ Lección completada. Escribe /siguiente para otra píldora o espera la de mañana."
        )
        self.store.move(lesson, LessonState.COMPLETED)

    def _send(self, text: str) -> None:
        self.messenger.send_message(self.chat_id, text)


def _format_pill(pill: Pill) -> str:
    return (
        f"📰 {pill.headline}\n\n"
        f"{pill.what_happened}\n\n"
        f"💡 Por qué importa: {pill.why_it_matters}\n\n"
        f"🔗 {pill.source_url}\n\n"
        f"🧠 Desafío: {pill.challenge}\n\n"
        "Responde aquí con tu análisis (3–6 frases)."
    )
