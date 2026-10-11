"""Almacén de lecciones y valores de control. Funciona con SQLite (local / caché de Actions) o con
Postgres (Supabase), según la URL: `sqlite:///ruta.db` o `postgresql://...`.

Las consultas se escriben con `?` y se adaptan a `%s` para Postgres.
"""

import json
import re
import sqlite3
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from nutricion.domain.lesson import Lesson, LessonState, Pill, transition
from nutricion.domain.progress import Score
from nutricion.memory.diagnose import explain_connection_error

_COLUMNS = """
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
"""
_KV = "CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
_EVENTS = (
    "CREATE TABLE IF NOT EXISTS events (id {id_type} PRIMARY KEY, created_at TEXT NOT NULL,"
    " kind TEXT NOT NULL, message TEXT NOT NULL, detail TEXT NOT NULL DEFAULT '')"
)
MAX_EVENTS = 200
_LESSONS = "CREATE TABLE IF NOT EXISTS lessons (id {id_type} PRIMARY KEY, {columns})"
_SCHEMAS = {
    "sqlite": _LESSONS.format(id_type="INTEGER", columns=_COLUMNS),
    "postgres": _LESSONS.format(id_type="BIGSERIAL", columns=_COLUMNS),
}

# Columnas añadidas después de la primera versión: se agregan a bases de datos ya existentes
_MIGRATIONS = {
    "source_name": "TEXT NOT NULL DEFAULT ''",
    "category": "TEXT NOT NULL DEFAULT ''",
    "image_url": "TEXT NOT NULL DEFAULT ''",
    "options": "TEXT NOT NULL DEFAULT '[]'",
    "choice": "TEXT NOT NULL DEFAULT ''",
    "source_title": "TEXT NOT NULL DEFAULT ''",
    "comprension": "INTEGER",
    "razonamiento": "INTEGER",
    "negocio": "INTEGER",
    "completed_at": "TEXT",
    "key_figure": "TEXT NOT NULL DEFAULT ''",
    "key_figure_label": "TEXT NOT NULL DEFAULT ''",
    "angle": "TEXT NOT NULL DEFAULT ''",
    "glossary": "TEXT NOT NULL DEFAULT '[]'",
}

_OPEN_STATES = (LessonState.PENDING, LessonState.AWAITING_ANSWER, LessonState.EVALUATING)
_SCORE_TEXT = re.compile(r"Comprensión (\d)/5 · Razonamiento (\d)/5 · Negocio (\d)/5")


class DatabaseConnectionError(Exception):
    """Fallo al conectar, con una explicación en español de la causa probable."""


class Store:
    def __init__(self, url: str) -> None:
        if url.startswith(("postgres://", "postgresql://")):
            import psycopg

            try:
                # prepare_threshold=None: compatible con el pooler de Supabase (pgbouncer)
                self._db = psycopg.connect(
                    url, autocommit=True, prepare_threshold=None, connect_timeout=15
                )
            except psycopg.Error as exc:
                raise DatabaseConnectionError(explain_connection_error(url, exc)) from None
            self._dialect = "postgres"
        else:
            path = url.removeprefix("sqlite:///")
            if path != ":memory:":
                Path(path).parent.mkdir(parents=True, exist_ok=True)
            self._db = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
            self._dialect = "sqlite"
        self._run(_SCHEMAS[self._dialect])
        self._run(_KV)
        self._run(_EVENTS.format(id_type="INTEGER" if self._dialect == "sqlite" else "BIGSERIAL"))
        self._migrate()

    def close(self) -> None:
        self._db.close()

    # --- acceso genérico -------------------------------------------------------------------

    def _run(self, sql: str, params: tuple = ()):
        if self._dialect == "postgres":
            sql = sql.replace("?", "%s")
        cursor = self._db.cursor()
        cursor.execute(sql, params)
        return cursor

    def _rows(self, sql: str, params: tuple = ()) -> list[dict]:
        cursor = self._run(sql, params)
        names = [d[0] for d in cursor.description]
        return [dict(zip(names, row, strict=True)) for row in cursor.fetchall()]

    def _migrate(self) -> None:
        existing = {d[0] for d in self._run("SELECT * FROM lessons LIMIT 0").description}
        for column, definition in _MIGRATIONS.items():
            if column not in existing:
                self._run(f"ALTER TABLE lessons ADD COLUMN {column} {definition}")
        # Lecciones evaluadas antes de guardar las notas por separado: se extraen del texto
        for row in self._rows(
            "SELECT id, scores FROM lessons WHERE scores IS NOT NULL AND comprension IS NULL"
        ):
            if match := _SCORE_TEXT.search(row["scores"] or ""):
                self._run(
                    "UPDATE lessons SET comprension = ?, razonamiento = ?, negocio = ?,"
                    " completed_at = COALESCE(completed_at, created_at) WHERE id = ?",
                    (*map(int, match.groups()), row["id"]),
                )

    # --- lecciones ------------------------------------------------------------------------

    def add_lesson(self, pill: Pill, source_title: str = "") -> Lesson:
        cursor = self._run(
            "INSERT INTO lessons (created_at, headline, what_happened, why_it_matters,"
            " source_url, challenge, state, source_name, category, image_url, options,"
            " source_title, key_figure, key_figure_label, angle, glossary)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING id",
            (
                _now(),
                pill.headline,
                pill.what_happened,
                pill.why_it_matters,
                pill.source_url,
                pill.challenge,
                str(LessonState.PENDING),
                pill.source_name,
                pill.category,
                pill.image_url,
                json.dumps(list(pill.options), ensure_ascii=False),
                source_title,
                pill.key_figure,
                pill.key_figure_label,
                pill.angle,
                json.dumps([list(e) for e in pill.glossary], ensure_ascii=False),
            ),
        )
        lesson_id = cursor.fetchone()[0]
        return Lesson(id=lesson_id, pill=pill, state=LessonState.PENDING)

    def open_lesson(self) -> Lesson | None:
        """La lección en curso (como mucho hay una), o None si todas están completadas."""
        placeholders = ",".join("?" * len(_OPEN_STATES))
        rows = self._rows(
            f"SELECT * FROM lessons WHERE state IN ({placeholders}) ORDER BY id DESC LIMIT 1",
            tuple(str(s) for s in _OPEN_STATES),
        )
        return _to_lesson(rows[0]) if rows else None

    def recent_pills(self, limit: int = 5) -> list[Pill]:
        """Las últimas píldoras enviadas o generadas, de la más reciente a la más antigua."""
        rows = self._rows("SELECT * FROM lessons ORDER BY id DESC LIMIT ?", (limit,))
        return [_to_lesson(r).pill for r in rows]

    def count_lessons(self) -> int:
        return self._run("SELECT COUNT(*) FROM lessons").fetchone()[0]

    def move(self, lesson: Lesson, target: LessonState) -> Lesson:
        new_state = transition(lesson.state, target)
        self._run("UPDATE lessons SET state = ? WHERE id = ?", (str(new_state), lesson.id))
        return replace(lesson, state=new_state)

    def save_choice(self, lesson: Lesson, choice: str) -> Lesson:
        self._run("UPDATE lessons SET choice = ? WHERE id = ?", (choice, lesson.id))
        return replace(lesson, choice=choice)

    def save_answer(self, lesson: Lesson, answer: str) -> None:
        self._run("UPDATE lessons SET answer = ? WHERE id = ?", (answer, lesson.id))

    def save_evaluation(self, lesson: Lesson, feedback: str, score: Score) -> None:
        self._run(
            "UPDATE lessons SET feedback = ?, scores = ?, comprension = ?, razonamiento = ?,"
            " negocio = ?, completed_at = ? WHERE id = ?",
            (
                feedback,
                score.line(),
                score.comprension,
                score.razonamiento,
                score.negocio,
                _now(),
                lesson.id,
            ),
        )

    def scores(self) -> list[tuple[datetime, Score]]:
        """Notas de las lecciones completadas, en orden cronológico."""
        rows = self._rows(
            "SELECT completed_at, comprension, razonamiento, negocio FROM lessons"
            " WHERE comprension IS NOT NULL ORDER BY completed_at"
        )
        return [
            (
                datetime.fromisoformat(r["completed_at"]),
                Score(r["comprension"], r["razonamiento"], r["negocio"]),
            )
            for r in rows
        ]

    def seen_urls(self) -> set[str]:
        return {r["source_url"] for r in self._rows("SELECT source_url FROM lessons")}

    def seen_titles(self) -> set[str]:
        rows = self._rows("SELECT source_title FROM lessons WHERE source_title != ''")
        return {r["source_title"] for r in rows}

    # --- valores de control ---------------------------------------------------------------

    # --- eventos (errores y reportes del usuario) -----------------------------------------

    def log_event(self, kind: str, message: str, detail: str = "") -> None:
        """Registra un error o un reporte; conserva solo los MAX_EVENTS más recientes."""
        self._run(
            "INSERT INTO events (created_at, kind, message, detail) VALUES (?, ?, ?, ?)",
            (_now(), kind, message[:1000], detail[:8000]),
        )
        self._run(
            "DELETE FROM events WHERE id NOT IN (SELECT id FROM events ORDER BY id DESC LIMIT ?)",
            (MAX_EVENTS,),
        )

    def recent_events(self, limit: int = 15) -> list[dict]:
        return self._rows(
            "SELECT id, created_at, kind, message, detail FROM events ORDER BY id DESC LIMIT ?",
            (limit,),
        )

    def get(self, key: str) -> str | None:
        row = self._run("SELECT value FROM kv WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None

    def set(self, key: str, value: str) -> None:
        self._run(
            "INSERT INTO kv (key, value) VALUES (?, ?)"
            " ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )

    # --- migración entre bases de datos ---------------------------------------------------

    def import_from(self, other: "Store") -> int:
        """Copia lecciones y valores de otra base (p. ej. SQLite de Actions -> Supabase)."""
        copied = 0
        known = self.seen_urls()
        columns = ["created_at", "source_url", *_COLUMN_NAMES, *_MIGRATIONS]
        for row in other._rows("SELECT * FROM lessons ORDER BY id"):
            if row["source_url"] in known:
                continue
            values = tuple(row.get(c) for c in columns)
            self._run(
                f"INSERT INTO lessons ({', '.join(columns)})"
                f" VALUES ({', '.join('?' * len(columns))})",
                values,
            )
            copied += 1
        for row in other._rows("SELECT key, value FROM kv"):
            if self.get(row["key"]) is None:
                self.set(row["key"], row["value"])
        return copied


_COLUMN_NAMES = [
    "headline",
    "what_happened",
    "why_it_matters",
    "challenge",
    "state",
    "answer",
    "feedback",
    "scores",
]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _to_lesson(row: dict) -> Lesson:
    pill = Pill(
        headline=row["headline"],
        what_happened=row["what_happened"],
        why_it_matters=row["why_it_matters"],
        source_url=row["source_url"],
        challenge=row["challenge"],
        source_name=row["source_name"],
        category=row["category"],
        image_url=row["image_url"],
        options=tuple(json.loads(row["options"])),
        key_figure=row.get("key_figure") or "",
        key_figure_label=row.get("key_figure_label") or "",
        angle=row.get("angle") or "",
        glossary=tuple(tuple(e) for e in json.loads(row.get("glossary") or "[]")),
    )
    return Lesson(id=row["id"], pill=pill, state=LessonState(row["state"]), choice=row["choice"])
