"""Almacén SQLite de lecciones y pequeños valores de control (p. ej. el offset de Telegram)."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from nutricion.domain.lesson import Lesson, LessonState, Pill, transition

_SCHEMA = """
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    headline TEXT NOT NULL,
    what_happened TEXT NOT NULL,
    why_it_matters TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    challenge TEXT NOT NULL,
    state TEXT NOT NULL,
    answer TEXT,
    feedback TEXT,
    scores TEXT
);
CREATE TABLE IF NOT EXISTS kv (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

_OPEN_STATES = (LessonState.PENDING, LessonState.AWAITING_ANSWER, LessonState.EVALUATING)


class Store:
    def __init__(self, path: str) -> None:
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path)
        self._db.row_factory = sqlite3.Row
        self._db.executescript(_SCHEMA)

    def add_lesson(self, pill: Pill) -> Lesson:
        with self._db:
            cur = self._db.execute(
                "INSERT INTO lessons (created_at, headline, what_happened, why_it_matters,"
                " source_url, challenge, state) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    datetime.now(UTC).isoformat(),
                    pill.headline,
                    pill.what_happened,
                    pill.why_it_matters,
                    pill.source_url,
                    pill.challenge,
                    LessonState.PENDING,
                ),
            )
        return Lesson(id=cur.lastrowid, pill=pill, state=LessonState.PENDING)

    def open_lesson(self) -> Lesson | None:
        """La lección en curso (como mucho hay una), o None si todas están completadas."""
        placeholders = ",".join("?" * len(_OPEN_STATES))
        row = self._db.execute(
            f"SELECT * FROM lessons WHERE state IN ({placeholders}) ORDER BY id DESC LIMIT 1",
            _OPEN_STATES,
        ).fetchone()
        return _to_lesson(row) if row else None

    def move(self, lesson: Lesson, target: LessonState) -> Lesson:
        new_state = transition(lesson.state, target)
        with self._db:
            self._db.execute("UPDATE lessons SET state = ? WHERE id = ?", (new_state, lesson.id))
        return Lesson(id=lesson.id, pill=lesson.pill, state=new_state)

    def save_answer(self, lesson: Lesson, answer: str) -> None:
        with self._db:
            self._db.execute("UPDATE lessons SET answer = ? WHERE id = ?", (answer, lesson.id))

    def save_feedback(self, lesson: Lesson, feedback: str, scores: str) -> None:
        with self._db:
            self._db.execute(
                "UPDATE lessons SET feedback = ?, scores = ? WHERE id = ?",
                (feedback, scores, lesson.id),
            )

    def seen_urls(self) -> set[str]:
        return {row[0] for row in self._db.execute("SELECT source_url FROM lessons")}

    def get(self, key: str) -> str | None:
        row = self._db.execute("SELECT value FROM kv WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None

    def set(self, key: str, value: str) -> None:
        with self._db:
            self._db.execute(
                "INSERT INTO kv (key, value) VALUES (?, ?)"
                " ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )


def _to_lesson(row: sqlite3.Row) -> Lesson:
    pill = Pill(
        headline=row["headline"],
        what_happened=row["what_happened"],
        why_it_matters=row["why_it_matters"],
        source_url=row["source_url"],
        challenge=row["challenge"],
    )
    return Lesson(id=row["id"], pill=pill, state=LessonState(row["state"]))
