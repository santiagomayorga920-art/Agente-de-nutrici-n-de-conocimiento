"""Formato HTML de Telegram para píldoras y feedback (todo el texto del LLM se escapa)."""

from html import escape

from nutricion.domain.lesson import Pill

CATEGORY_ICONS = {"Negocios": "💼", "Finanzas": "📈", "Investigación": "🔬"}


def pill_header(pill: Pill) -> str:
    icon = CATEGORY_ICONS.get(pill.category, "📰")
    origin = " · ".join(p for p in (pill.category, pill.source_name) if p)
    return f"{icon} <b>{escape(pill.headline)}</b>\n<i>{escape(origin)}</i>"


def pill_body(pill: Pill) -> str:
    return (
        f"<b>Qué pasó</b>\n{escape(pill.what_happened)}\n\n"
        f"<b>Por qué importa</b>\n{escape(pill.why_it_matters)}\n\n"
        f'🔗 <a href="{escape(pill.source_url, quote=True)}">Leer la fuente</a>\n\n'
        f"🧠 <b>Desafío</b>\n{escape(pill.challenge)}\n\n"
        + (
            "<i>Elige una postura con los botones o responde directamente por escrito.</i>"
            if pill.options
            else "<i>Responde aquí con tu análisis (3–6 frases).</i>"
        )
    )


def reminder(pill: Pill) -> str:
    header = pill_header(pill)
    return f"⏳ <b>Tienes un desafío pendiente</b>\n\n{header}\n\n🧠 {escape(pill.challenge)}"


def choice_reaction(choice: str, reaction: str) -> str:
    return (
        f"Elegiste: <b>{escape(choice)}</b>\n\n{escape(reaction)}\n\n"
        "<i>✍️ Escribe tu justificación para recibir la evaluación.</i>"
    )


def feedback(scores_line: str, text: str) -> str:
    return f"📊 <b>{escape(scores_line)}</b>\n\n{escape(text)}\n\n✅ <b>Lección completada.</b>"


def plain(text: str) -> str:
    return escape(text)
