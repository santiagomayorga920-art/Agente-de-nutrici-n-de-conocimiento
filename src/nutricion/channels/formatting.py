"""Formato HTML de Telegram para píldoras y feedback (todo el texto del LLM se escapa)."""

from html import escape

from nutricion.domain.lesson import Pill
from nutricion.domain.progress import Profile, Score

CATEGORY_ICONS = {"Negocios": "💼", "Finanzas": "📈", "Investigación": "🔬"}


def pill_header(pill: Pill) -> str:
    icon = CATEGORY_ICONS.get(pill.category, "📰")
    origin = " · ".join(p for p in (pill.category, pill.source_name) if p)
    return f"{icon} <b>{escape(pill.headline)}</b>\n<i>{escape(origin)}</i>"


def pill_body(pill: Pill) -> str:
    return (
        f"<b>Qué pasó</b>\n{escape(pill.what_happened)}\n\n"
        f"<b>Por qué importa</b>\n{escape(pill.why_it_matters)}\n\n"
        + glossary(pill)
        + f'🔗 <a href="{escape(pill.source_url, quote=True)}">Leer la fuente</a>\n\n'
        f"🧠 <b>Desafío</b>\n{escape(pill.challenge)}\n\n"
        + (
            "<i>Elige una postura con los botones o responde directamente por escrito.</i>"
            if pill.options
            else "<i>Responde aquí con tu análisis (3–6 frases).</i>"
        )
    )


def glossary(pill: Pill) -> str:
    if not pill.glossary:
        return ""
    lines = "\n".join(f"• <b>{escape(t)}</b>: {escape(d)}" for t, d in pill.glossary)
    return f"📖 <b>Glosario rápido</b>\n{lines}\n\n"


def reminder(pill: Pill) -> str:
    header = pill_header(pill)
    return f"⏳ <b>Tienes un desafío pendiente</b>\n\n{header}\n\n🧠 {escape(pill.challenge)}"


def choice_reaction(choice: str, reaction: str) -> str:
    return (
        f"Elegiste: <b>{escape(choice)}</b>\n\n{escape(reaction)}\n\n"
        "<i>✍️ Escribe tu justificación para recibir la evaluación.</i>"
    )


def feedback(score: Score, text: str, profile: Profile) -> str:
    return (
        f"📊 <b>{escape(score.line())}</b>\n\n{escape(text)}\n\n"
        f"✅ <b>Lección completada.</b> {progress_line(profile)}"
    )


def progress_line(profile: Profile) -> str:
    parts = [f"📚 {profile.completed}", f"🔥 {profile.streak} {_days(profile.streak)}"]
    if profile.next_level:
        parts.append(f"{profile.to_next_level} para {escape(profile.next_level)}")
    return " · ".join(parts)


def profile_card(profile: Profile) -> str:
    if not profile.completed:
        return (
            "👤 <b>Tu perfil</b>\n"
            f"Nivel: {escape(profile.level)}\n"
            "Aún no has completado ninguna píldora. ¡La primera te espera!"
        )
    lines = [
        "👤 <b>Tu perfil</b>",
        f"Nivel: <b>{escape(profile.level)}</b>",
        f"📚 Píldoras completadas: <b>{profile.completed}</b>",
        f"🔥 Racha: <b>{profile.streak} {_days(profile.streak)}</b>",
        "",
        f"⭐ Promedio general: <b>{profile.average:.1f}/5</b>",
        f"   Comprensión {_bar(profile.avg_comprension)} {profile.avg_comprension:.1f}",
        f"   Razonamiento {_bar(profile.avg_razonamiento)} {profile.avg_razonamiento:.1f}",
        f"   Negocio {_bar(profile.avg_negocio)} {profile.avg_negocio:.1f}",
    ]
    if profile.next_level:
        lines += ["", f"🎯 Te faltan {profile.to_next_level} para {escape(profile.next_level)}"]
    if profile.weakest:
        lines.append(f"💪 Punto a reforzar: <b>{profile.weakest}</b>")
    return "\n".join(lines)


def _bar(value: float) -> str:
    filled = round(value)
    return "▰" * filled + "▱" * (5 - filled)


def _days(n: int) -> str:
    return "día" if n == 1 else "días"


def plain(text: str) -> str:
    return escape(text)
