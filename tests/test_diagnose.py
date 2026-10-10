import pytest

from nutricion.memory.diagnose import database_url_problems, explain_connection_error
from nutricion.memory.store import DatabaseConnectionError, Store

GOOD = "postgresql://postgres.abcdefghij:Clave123@aws-0-us-east-1.pooler.supabase.com:5432/postgres"


def test_correct_session_pooler_uri_has_no_problems():
    assert database_url_problems(GOOD) == []


@pytest.mark.parametrize(
    ("url", "hint"),
    [
        (
            "postgresql://postgres:Clave123@aws-0-us-east-1.pooler.supabase.com:5432/postgres",
            "postgres.<id-del-proyecto>",
        ),
        (
            "postgresql://postgres.abc:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres",
            "corchetes",
        ),
        (
            "postgresql://postgres.abc:mi@clave@aws-0-us-east-1.pooler.supabase.com:5432/postgres",
            "más de una @",
        ),
        ("postgresql://postgres:Clave@db.abc.supabase.co:5432/postgres", "IPv6"),
        (
            "postgresql://postgres.abc:Clave@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
            "Session pooler (5432)",
        ),
        ("https://supabase.com/dashboard", "postgresql://"),
    ],
)
def test_common_mistakes_are_explained(url, hint):
    assert any(hint in p for p in database_url_problems(url))


def test_wrong_password_is_explained_without_leaking_it():
    message = explain_connection_error(
        GOOD, Exception('FATAL: password authentication failed for user "postgres.abc"')
    )
    assert "Restablécela" in message and "Clave123" not in message


def test_unreachable_postgres_raises_a_readable_error():
    with pytest.raises(DatabaseConnectionError, match="No se pudo conectar"):
        Store("postgresql://postgres:x@127.0.0.1:1/postgres")


def test_password_variable_fills_the_supabase_template():
    from nutricion.config import Settings

    template = "postgresql://postgres.abc:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres"
    settings = Settings(_env_file=None, database_url=template, database_password="mi@clave#1")
    assert settings.database == (
        "postgresql://postgres.abc:mi%40clave%231@aws-0-us-east-1.pooler.supabase.com:5432/postgres"
    )
    assert database_url_problems(settings.database) == []


def test_url_without_template_is_left_alone():
    from nutricion.config import Settings

    settings = Settings(_env_file=None, database_url=GOOD, database_password="otra")
    assert settings.database == GOOD
