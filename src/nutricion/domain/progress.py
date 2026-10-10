"""Gamificación: notas, promedios, racha de días y nivel del estudiante (sin dependencias)."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

# (píldoras completadas necesarias, nombre del nivel)
LEVELS = [
    (0, "🌱 Aprendiz"),
    (5, "📊 Analista"),
    (15, "♟️ Estratega"),
    (30, "🚀 Visionario"),
    (60, "🏛️ Maestro"),
]


def _clamp(n: int) -> int:
    return min(max(int(n), 1), 5)


@dataclass(frozen=True)
class Score:
    comprension: int
    razonamiento: int
    negocio: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "comprension", _clamp(self.comprension))
        object.__setattr__(self, "razonamiento", _clamp(self.razonamiento))
        object.__setattr__(self, "negocio", _clamp(self.negocio))

    @property
    def total(self) -> float:
        return (self.comprension + self.razonamiento + self.negocio) / 3

    def line(self) -> str:
        return (
            f"Comprensión {self.comprension}/5 · "
            f"Razonamiento {self.razonamiento}/5 · "
            f"Negocio {self.negocio}/5"
        )


@dataclass(frozen=True)
class Profile:
    completed: int
    avg_comprension: float
    avg_razonamiento: float
    avg_negocio: float
    streak: int
    level: str
    next_level: str | None
    to_next_level: int
    last_score: float | None

    @property
    def average(self) -> float:
        return (self.avg_comprension + self.avg_razonamiento + self.avg_negocio) / 3

    @property
    def weakest(self) -> str | None:
        if not self.completed:
            return None
        criteria = {
            "Comprensión": self.avg_comprension,
            "Razonamiento": self.avg_razonamiento,
            "Negocio": self.avg_negocio,
        }
        return min(criteria, key=criteria.get)


def build_profile(
    scores: list[tuple[datetime, Score]], today: date | None = None, tz: str = "UTC"
) -> Profile:
    zone = ZoneInfo(tz)
    n = len(scores)

    def avg(attr: str) -> float:
        return sum(getattr(s, attr) for _, s in scores) / n if n else 0.0

    days = {when.astimezone(zone).date() for when, _ in scores}
    today = today or datetime.now(zone).date()
    streak = _streak(days, today)

    level, next_level, to_next = LEVELS[0][1], None, 0
    for i, (needed, name) in enumerate(LEVELS):
        if n >= needed:
            level = name
            if i + 1 < len(LEVELS):
                next_level, to_next = LEVELS[i + 1][1], LEVELS[i + 1][0] - n
            else:
                next_level, to_next = None, 0

    return Profile(
        completed=n,
        avg_comprension=avg("comprension"),
        avg_razonamiento=avg("razonamiento"),
        avg_negocio=avg("negocio"),
        streak=streak,
        level=level,
        next_level=next_level,
        to_next_level=to_next,
        last_score=scores[-1][1].total if scores else None,
    )


def _streak(days: set[date], today: date) -> int:
    """Días seguidos con al menos una lección; hoy aún sin lección no rompe la racha."""
    day = today if today in days else today - timedelta(days=1)
    streak = 0
    while day in days:
        streak += 1
        day -= timedelta(days=1)
    return streak
