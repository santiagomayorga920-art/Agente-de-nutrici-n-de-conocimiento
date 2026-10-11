"""Pruebas del almacén con SQLite y, si TEST_DATABASE_URL está definida (CI), con Postgres."""

import os
import sqlite3

import pytest

from nutricion.domain.lesson import LessonState, Pill
from nutricion.domain.progress import Score
from nutricion.memory.store import Store

BACKENDS = ["sqlite:///:memory:"]
if os.environ.get("TEST_DATABASE_URL"):
    BACKENDS.append(os.environ["TEST_DATABASE_URL"])


@pytest.fixture(params=BACKENDS)
def store(request):
    store = Store(request.param)
    if request.param.startswith("postgres"):
        store._run("TRUNCATE lessons, kv RESTART IDENTITY")
    yield store
    store.close()


def pill(url: str = "https://a") -> Pill:
    return Pill("T", "W", "Y", url, "C", "Fuente", "Negocios", "", ("Sí", "No"))


def test_lesson_lifecycle_and_scores(store):
    lesson = store.add_lesson(pill(), "titulo normalizado")
    assert lesson.id == 1
    lesson = store.move(lesson, LessonState.AWAITING_ANSWER)
    lesson = store.save_choice(lesson, "Sí")
    assert store.open_lesson() == lesson
    store.save_answer(lesson, "respuesta")
    store.save_evaluation(lesson, "bien", Score(4, 3, 5))
    store.move(store.move(lesson, LessonState.EVALUATING), LessonState.COMPLETED)
    assert store.open_lesson() is None
    [(when, score)] = store.scores()
    assert score == Score(4, 3, 5) and when.tzinfo is not None
    assert store.seen_urls() == {"https://a"}
    assert store.seen_titles() == {"titulo normalizado"}


def test_kv_upsert(store):
    store.set("k", "1")
    store.set("k", "2")
    assert store.get("k") == "2" and store.get("otra") is None


def test_import_from_sqlite_keeps_scores_and_skips_duplicates(store, tmp_path):
    origin = Store(f"sqlite:///{tmp_path / 'origen.db'}")
    first = origin.add_lesson(pill("https://x"))
    origin.save_evaluation(first, "ok", Score(4, 3, 3))
    origin.set("telegram_offset", "42")
    assert store.import_from(origin) == 1
    assert store.import_from(origin) == 0
    assert store.scores()[0][1] == Score(4, 3, 3)
    assert store.get("telegram_offset") == "42"
    origin.close()


def test_old_database_scores_are_backfilled(tmp_path):
    path = tmp_path / "v1.db"
    db = sqlite3.connect(path)
    db.executescript(
        "CREATE TABLE lessons (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,"
        " headline TEXT NOT NULL, what_happened TEXT NOT NULL, why_it_matters TEXT NOT NULL,"
        " source_url TEXT NOT NULL UNIQUE, challenge TEXT NOT NULL, state TEXT NOT NULL,"
        " answer TEXT, feedback TEXT, scores TEXT);"
        "INSERT INTO lessons VALUES (1, '2026-10-10T13:00:00+00:00', 'h', 'w', 'y', 'https://u',"
        " 'c', 'completed', 'r', 'f', 'Comprensión 4/5 · Razonamiento 3/5 · Negocio 3/5');"
    )
    db.commit()
    db.close()
    store = Store(f"sqlite:///{path}")
    assert store.scores()[0][1] == Score(4, 3, 3)


def test_events_are_kept_newest_first_and_capped(store, monkeypatch):
    import nutricion.memory.store as module

    monkeypatch.setattr(module, "MAX_EVENTS", 3)
    for i in range(5):
        store.log_event("error", f"e{i}", "detalle")
    events = store.recent_events(10)
    assert [e["message"] for e in events] == ["e4", "e3", "e2"]
