"""Diagnóstico en español de una DATABASE_URL de Postgres/Supabase (sin mostrar la contraseña)."""

from urllib.parse import urlsplit

POOLER_HOST = "pooler.supabase.com"


def database_url_problems(url: str) -> list[str]:
    """Errores típicos al copiar la URI de Supabase. Lista vacía si no se detecta ninguno."""
    if not url.startswith(("postgres://", "postgresql://")):
        return ["Debe empezar por postgresql:// (copia la URI desde Supabase → Connect)."]
    problems = []
    if "[" in url or "]" in url or "YOUR-PASSWORD" in url.upper():
        problems.append(
            "Contiene corchetes o el texto [YOUR-PASSWORD]. Lo más fácil: deja la URI tal cual"
            " y crea la variable DATABASE_PASSWORD con tu contraseña; el bot la inserta sola."
        )
    if url.count("@") > 1:
        problems.append(
            "Hay más de una @: tu contraseña contiene símbolos especiales. Restablécela en"
            " Supabase (Project Settings → Database) usando solo letras y números."
        )
    try:
        parts = urlsplit(url)
        host, user, port = parts.hostname or "", parts.username or "", parts.port
    except ValueError:
        return [*problems, "La URI está mal formada (¿la contraseña tiene # / ? o %?)."]
    if parts.fragment or parts.query.count("?"):
        problems.append("La contraseña parece contener # o ?: usa solo letras y números.")
    if host.endswith(POOLER_HOST) and "." not in user:
        problems.append(
            f"El usuario es «{user}» pero el pooler de Supabase exige «{user}.<id-del-proyecto>"
            "» (p. ej. postgres.abcdefghijklmnop). Copia la URI completa desde Connect →"
            " Session pooler, sin editar el usuario."
        )
    if host.startswith("db.") and host.endswith(".supabase.co"):
        problems.append(
            "Es la conexión directa (db.xxx.supabase.co), que solo funciona por IPv6 y falla"
            " en GitHub Actions y Render. Usa la URI de Connect → Session pooler."
        )
    if host.endswith(POOLER_HOST) and port == 6543:
        problems.append("El puerto 6543 es el Transaction pooler; usa el Session pooler (5432).")
    return problems


def explain_connection_error(url: str, error: Exception) -> str:
    problems = database_url_problems(url)
    message = str(error).lower()
    if not problems and "password authentication failed" in message:
        problems.append(
            "Supabase rechazó la contraseña. Restablécela en Project Settings → Database"
            " (solo letras y números) y vuelve a copiar la URI del Session pooler."
        )
    if not problems and "tenant or user not found" in message:
        problems.append("Supabase no encuentra el proyecto: revisa el usuario postgres.<id>.")
    if not problems:
        problems.append(f"Error de conexión: {error.__class__.__name__}.")
    return "No se pudo conectar a la base de datos (DATABASE_URL):\n- " + "\n- ".join(problems)
