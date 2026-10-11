"""Orquestador del agente. Cada actualización de Telegram (mensaje o botón) pasa por
`handle_update`, venga del sondeo programado (`tick`) o del webhook en tiempo real.
"""

import json
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Protocol
from zoneinfo import ZoneInfo

import httpx

from nutricion.agents import researcher, tutor
from nutricion.channels import formatting as fmt
from nutricion.channels.telegram import TelegramError
from nutricion.domain.lesson import Lesson, LessonState, Pill
from nutricion.domain.progress import Profile, build_profile
from nutricion.llm import LLMClient
from nutricion.media import card
from nutricion.media.voice import Voice
from nutricion.memory.store import Store
from nutricion.sources import feeds, images
from nutricion.sources.catalog import category_of_the_day

OFFSET_KEY = "telegram_offset"
DAILY_KEY = "ultima_pildora_diaria"
# Tras un /reportar sin texto, el siguiente mensaje se guarda como su descripción
REPORT_PENDING_KEY = "reporte_pendiente"
NEXT = "next"
OPTION_PREFIX = "op"
# EVALUATING también admite respuesta: un intento anterior pudo fallar a mitad de la evaluación
_ANSWERABLE = (LessonState.AWAITING_ANSWER, LessonState.EVALUATING)
_NEXT_BUTTON = [("➡️ Siguiente píldora", NEXT)]
CAPTION_LIMIT = 1024

COMMANDS = [
    ("siguiente", "Recibir una nueva píldora"),
    ("stats", "Ver tu perfil y estadísticas"),
    ("reportar", "Reportar un problema (escribe qué pasó)"),
]
REPORT_BUTTON = [("🛠 Reportar problema", "report")]
WELCOME = (
    "¡Hola! Soy tu agente de nutrición de conocimiento. Cada día te enviaré una píldora sobre IA"
    " y negocios con un desafío. Elige una postura con los botones o respóndelo por escrito y te"
    " daré feedback.\n\nComandos: /siguiente para una nueva píldora · /stats para tu perfil ·"
    " /reportar si algo falla."
)
VOICE_CAPTION = "🎧 Escucha la píldora"
NO_PENDING = (
    "No tienes ningún desafío pendiente. Escribe /siguiente para recibir una nueva píldora."
)


class Messenger(Protocol):
    def get_updates(self, offset: int) -> list[dict]: ...

    def send_message(self, chat_id: str, text: str, buttons=None) -> None: ...

    def send_photo(self, chat_id: str, photo_url: str, caption: str, buttons=None) -> None: ...

    def send_photo_file(self, chat_id: str, image: bytes, caption: str, buttons=None) -> None: ...

    def send_voice(self, chat_id: str, audio: bytes, duration: int, caption: str = "") -> None: ...

    def send_typing(self, chat_id: str, action: str = "typing") -> None: ...

    def answer_callback(self, callback_id: str, text: str = "") -> None: ...

    def remove_buttons(self, chat_id: str, message_id: int) -> None: ...


@dataclass
class Agent:
    store: Store
    llm: LLMClient
    messenger: Messenger
    chat_id: str
    fetch_candidates: Callable[[set[str]], list[feeds.Candidate]] = feeds.fetch_candidates
    find_image: Callable[[str], str] = field(default=images.find_og_image)
    make_card: Callable[[Pill, str], bytes | None] = field(default=card.build_card)
    # Nota de voz de la píldora; None la desactiva (la fábrica la conecta con Gemini)
    make_voice: Callable[[Pill], Voice] | None = None
    timezone: str = "UTC"

    # --- entradas -------------------------------------------------------------------------

    def tick(self, send_daily_pill: bool, poll: bool = True) -> None:
        """Ejecución programada: recoge actualizaciones (si no hay webhook) y la píldora diaria."""
        if poll:
            offset = int(self.store.get(OFFSET_KEY) or 0)
            for update in self.messenger.get_updates(offset):
                self.handle_update(update)
        if send_daily_pill:
            self.daily_pill_if_due()

    def handle_update(self, update: dict) -> None:
        update_id = update["update_id"]
        if update_id < int(self.store.get(OFFSET_KEY) or 0):
            return  # ya procesada (Telegram puede reenviar una actualización)
        if "callback_query" in update:
            self._handle_button(update["callback_query"])
        else:
            message = update.get("message") or {}
            text = (message.get("text") or "").strip()
            if str(message.get("chat", {}).get("id")) == self.chat_id and text:
                self._handle_text(text)
        # Se avanza tras procesar: si algo falla, se reintenta
        self.store.set(OFFSET_KEY, str(update_id + 1))

    def daily_pill_if_due(self, force: bool = False) -> bool:
        """Envía la píldora diaria una sola vez por día (en la zona horaria del usuario), aunque
        el disparador programado llegue repetido. Devuelve si la envió."""
        today = datetime.now(ZoneInfo(self.timezone)).date().isoformat()
        if not force and self.store.get(DAILY_KEY) == today:
            return False
        self.daily_pill()
        self.store.set(DAILY_KEY, today)
        return True

    def daily_pill(self) -> None:
        self._send(fmt.profile_card(self.profile()))
        lesson = self.store.open_lesson()
        if lesson and lesson.state in _ANSWERABLE:
            self._send(fmt.reminder(lesson.pill))
        else:
            self._deliver_new_pill()

    def profile(self) -> Profile:
        return build_profile(self.store.scores(), tz=self.timezone)

    # --- mensajes y botones ---------------------------------------------------------------

    def _handle_text(self, text: str) -> None:
        command = text.split()[0].lower().split("@")[0]
        lesson = self.store.open_lesson()
        if command == "/start":
            self._send(fmt.plain(WELCOME))
            self._send(fmt.profile_card(self.profile()))
        elif command == "/stats":
            self._send(fmt.profile_card(self.profile()))
        elif command == "/reportar":
            self.report(text.partition(" ")[2].strip())
        elif not command.startswith("/") and self.store.get(REPORT_PENDING_KEY):
            self.store.set(REPORT_PENDING_KEY, "")
            self.report(text)
        elif command == "/siguiente":
            self._next_pill(lesson)
        elif lesson and lesson.state in _ANSWERABLE:
            self._evaluate(lesson, text)
        else:
            self._send(fmt.plain(NO_PENDING))

    def _handle_button(self, query: dict) -> None:
        message = query.get("message") or {}
        if str(message.get("chat", {}).get("id")) != self.chat_id:
            return
        self.messenger.answer_callback(query["id"])
        self.messenger.remove_buttons(self.chat_id, message["message_id"])
        data = query.get("data", "")
        lesson = self.store.open_lesson()
        if data == NEXT:
            self._next_pill(lesson)
        elif data == "report":
            self.report("")
        elif data.startswith(OPTION_PREFIX + ":"):
            _, lesson_id, index = data.split(":")
            if not (lesson and lesson.id == int(lesson_id) and lesson.state in _ANSWERABLE):
                self._send("Ese desafío ya terminó. Escribe /siguiente para uno nuevo.")
                return
            if not 0 <= int(index) < len(lesson.pill.options):
                return
            choice = lesson.pill.options[int(index)]
            lesson = self.store.save_choice(lesson, choice)
            self.messenger.send_typing(self.chat_id)
            reaction = tutor.react_to_choice(self.llm, lesson.pill, choice)
            self._send(fmt.choice_reaction(choice, reaction))

    def report(self, description: str) -> None:
        """Guarda un reporte con el contexto necesario para diagnosticarlo."""
        lesson = self.store.open_lesson()
        errors = [e for e in self.store.recent_events(10) if e["kind"] == "error"][:3]
        context = {
            "leccion_abierta": {"id": lesson.id, "estado": str(lesson.state)} if lesson else None,
            "ultimos_errores": [f"{e['created_at']} {e['message']}" for e in errors],
        }
        self.store.log_event(
            "reporte",
            description or "(sin descripción)",
            json.dumps(context, ensure_ascii=False),
        )
        if description:
            self._send(
                "🛠 <b>Reporte recibido.</b> Quedó guardado con el estado del bot y los últimos"
                " errores para revisarlo. ¡Gracias!"
            )
        else:
            self.store.set(REPORT_PENDING_KEY, "1")
            self._send(
                "🛠 Reporte guardado. <b>¿Qué pasó?</b> Escríbelo en tu próximo mensaje y lo"
                " añado al reporte (p. ej. «pulsé Siguiente píldora y no llegó el audio»)."
            )

    def _next_pill(self, lesson: Lesson | None) -> None:
        if lesson and lesson.state in _ANSWERABLE:
            self._send(fmt.reminder(lesson.pill))
        else:
            self._deliver_new_pill()

    # --- píldoras -------------------------------------------------------------------------

    def _deliver_new_pill(self) -> None:
        steps = _Stopwatch()
        lesson = self.store.open_lesson()
        if not (lesson and lesson.state is LessonState.PENDING):
            # Si un envío anterior falló, se reutiliza esa píldora en vez de generar otra
            self.messenger.send_typing(self.chat_id)
            seen_titles = self.store.seen_titles()
            candidates = [
                c
                for c in self.fetch_candidates(self.store.seen_urls())
                if feeds.normalize_title(c.title) not in seen_titles
            ]
            if not candidates:
                raise feeds.NoNewsFound("Todas las noticias disponibles ya se enviaron")
            steps.lap("noticias")
            preferred = category_of_the_day(self.store.count_lessons())
            recent = self.store.recent_pills(researcher.HISTORY)
            pill, chosen = researcher.create_pill(self.llm, candidates, preferred, recent)
            steps.lap("redacción")
            if not pill.image_url:
                pill = replace(pill, image_url=self.find_image(pill.source_url))
            lesson = self.store.add_lesson(pill, feeds.normalize_title(chosen.title))
        self._send_pill(lesson, steps)
        self.store.move(lesson, LessonState.AWAITING_ANSWER)
        # Desglose para el diagnóstico: dice qué etapa hace lenta una píldora
        self.store.log_event("traza", f"píldora {lesson.id}: {steps}")

    def _send_pill(self, lesson: Lesson, steps: "_Stopwatch | None" = None) -> None:
        steps = steps or _Stopwatch()
        self._send_pill_visual(lesson)
        steps.lap("tarjeta y envío")
        self._send_voice(lesson.pill)
        steps.lap("voz")

    def _send_pill_visual(self, lesson: Lesson) -> None:
        pill = lesson.pill
        buttons = [(o, f"{OPTION_PREFIX}:{lesson.id}:{i}") for i, o in enumerate(pill.options)]
        header, body = fmt.pill_header(pill), fmt.pill_body(pill)
        full = f"{header}\n\n{body}"
        # 1) Tarjeta visual generada; 2) foto del artículo por URL; 3) solo texto
        image = self.make_card(pill, self.timezone)
        photos = [image] if image else []
        if pill.image_url:
            photos.append(pill.image_url)
        for photo in photos:
            # Una sola tarjeta si cabe en el pie de foto; si no, foto con titular y luego el texto
            if len(full) <= CAPTION_LIMIT:
                if self._try_photo(photo, full, buttons):
                    return
            elif self._try_photo(photo, header):
                self._send(body, buttons)
                return
        self._send(full, buttons)

    def _send_voice(self, pill: Pill) -> None:
        """La nota de voz es un extra: si falla, se registra un aviso y la píldora sigue."""
        if not self.make_voice:
            return
        self.messenger.send_typing(self.chat_id, "record_voice")
        try:
            voice = self.make_voice(pill)
            self.messenger.send_voice(self.chat_id, voice.audio, voice.duration, VOICE_CAPTION)
        except Exception:  # noqa: BLE001 - p. ej. cuota de voz agotada: no bloquea la lección
            self.store.log_event("aviso", "nota de voz no enviada", traceback.format_exc())

    def _try_photo(self, photo: bytes | str, caption: str, buttons=None) -> bool:
        try:
            if isinstance(photo, bytes):
                self.messenger.send_photo_file(self.chat_id, photo, caption, buttons)
            else:
                self.messenger.send_photo(self.chat_id, photo, caption, buttons)
            return True
        except (TelegramError, httpx.HTTPError):
            return False  # Telegram rechazó la imagen: se prueba la siguiente opción

    # --- evaluación -----------------------------------------------------------------------

    def _evaluate(self, lesson: Lesson, answer: str) -> None:
        self.store.save_answer(lesson, answer)
        if lesson.state is LessonState.AWAITING_ANSWER:
            lesson = self.store.move(lesson, LessonState.EVALUATING)
        self.messenger.send_typing(self.chat_id)
        try:
            evaluation = tutor.evaluate(self.llm, lesson.pill, answer, lesson.choice)
        except Exception:
            self.store.move(lesson, LessonState.AWAITING_ANSWER)
            raise
        score = evaluation.score()
        self.store.save_evaluation(lesson, evaluation.feedback, score)
        self.store.move(lesson, LessonState.COMPLETED)
        self._send(fmt.feedback(score, evaluation.feedback, self.profile()), _NEXT_BUTTON)

    def _send(self, text: str, buttons=None) -> None:
        self.messenger.send_message(self.chat_id, text, buttons)


class _Stopwatch:
    """Mide cuánto tarda cada etapa: «noticias 4.1 s · redacción 12.0 s · …»."""

    def __init__(self) -> None:
        self._last = time.monotonic()
        self._laps: list[str] = []

    def lap(self, name: str) -> None:
        now = time.monotonic()
        self._laps.append(f"{name} {now - self._last:.1f} s")
        self._last = now

    def __str__(self) -> str:
        return " · ".join(self._laps)
