from datetime import UTC, date, datetime

from nutricion.domain.progress import Score, build_profile


def at(day: int, hour: int = 12) -> datetime:
    return datetime(2026, 10, day, hour, tzinfo=UTC)


def test_scores_are_clamped():
    assert Score(9, 0, 3) == Score(5, 1, 3)


def test_empty_profile():
    profile = build_profile([], today=date(2026, 10, 10))
    assert profile.completed == 0 and profile.streak == 0 and profile.weakest is None
    assert profile.next_level and profile.to_next_level == 5


def test_averages_streak_and_level():
    scores = [(at(d), Score(4, 3, 2)) for d in (5, 7, 8, 9)] + [(at(9, 18), Score(2, 3, 4))]
    profile = build_profile(scores, today=date(2026, 10, 10))
    assert profile.completed == 5
    assert profile.avg_comprension == 3.6
    assert profile.streak == 3  # 7, 8 y 9; el 10 aún no ha terminado
    assert profile.level == "📊 Analista" and profile.to_next_level == 10
    assert profile.weakest == "Negocio"


def test_streak_breaks_after_a_missed_day():
    profile = build_profile([(at(7), Score(3, 3, 3))], today=date(2026, 10, 10))
    assert profile.streak == 0


def test_streak_uses_local_timezone():
    # 02:00 UTC del día 10 sigue siendo el día 9 en Bogotá (UTC-5)
    scores = [(at(9, 12), Score(3, 3, 3)), (at(10, 2), Score(3, 3, 3))]
    profile = build_profile(scores, today=date(2026, 10, 9), tz="America/Bogota")
    assert profile.streak == 1
