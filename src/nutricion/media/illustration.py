"""Ilustración generada con IA para el fondo de la tarjeta (v4.3).

Proveedores gratuitos, en orden:
1. Cloudflare Workers AI (FLUX.1 schnell), si hay CLOUDFLARE_ACCOUNT_ID y CLOUDFLARE_API_TOKEN:
   cuota diaria gratuita y muy estable.
2. Pollinations: sin cuenta ni clave; más lento y con límites por minuto.
Los textos de la tarjeta los dibuja Pillow encima: los modelos de imagen escriben letras
ilegibles, por eso aquí se les pide expresamente que no pongan texto.
"""

import base64
import random
from urllib.parse import quote

import httpx

from nutricion.domain.lesson import Pill

SIZE = 1024
TIMEOUT_S = 60
# Estilo común: coherente entre píldoras y apto para poner texto blanco encima
STYLE = (
    "editorial illustration for a business magazine, modern flat vector style, deep navy blue"
    " background, soft cinematic lighting, clean composition with empty space at the bottom,"
    " no text, no letters, no numbers, no logos, no watermark"
)
CLOUDFLARE_MODEL = "@cf/black-forest-labs/flux-1-schnell"
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/"


class IllustrationError(Exception):
    pass


def prompt_for(pill: Pill) -> str:
    scene = pill.image_prompt.strip() or (
        f"visual metaphor of this business news about artificial intelligence: {pill.headline}"
    )
    return f"{scene}. {STYLE}"


def cloudflare(prompt: str, account_id: str, token: str, http: httpx.Client) -> bytes:
    response = http.post(
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{CLOUDFLARE_MODEL}",
        headers={"Authorization": f"Bearer {token}"},
        json={"prompt": prompt, "steps": 4},
    )
    data = response.json() if response.content else {}
    image = (data.get("result") or {}).get("image")
    if response.status_code != 200 or not image:
        errors = data.get("errors") or response.status_code
        raise IllustrationError(f"Cloudflare: {errors}")
    return base64.b64decode(image)


def pollinations(prompt: str, http: httpx.Client) -> bytes:
    response = http.get(
        POLLINATIONS_URL + quote(prompt, safe=""),
        params={
            "width": SIZE,
            "height": SIZE,
            "model": "flux",
            "nologo": "true",
            "seed": random.randint(1, 1_000_000),
        },
        follow_redirects=True,
    )
    if response.status_code != 200 or not response.headers.get("content-type", "").startswith(
        "image/"
    ):
        raise IllustrationError(f"Pollinations: HTTP {response.status_code}")
    return response.content


def generate(
    prompt: str,
    cloudflare_account_id: str = "",
    cloudflare_token: str = "",
    http: httpx.Client | None = None,
) -> bytes:
    """Imagen (JPEG/PNG) del primer proveedor que responda; lanza IllustrationError si ninguno."""
    http = http or httpx.Client(timeout=TIMEOUT_S)
    problems: list[str] = []
    if cloudflare_account_id and cloudflare_token:
        try:
            return cloudflare(prompt, cloudflare_account_id, cloudflare_token, http)
        except (IllustrationError, httpx.HTTPError, ValueError) as exc:
            problems.append(str(exc) or type(exc).__name__)
    try:
        return pollinations(prompt, http)
    except (IllustrationError, httpx.HTTPError) as exc:
        problems.append(str(exc) or type(exc).__name__)
    raise IllustrationError("; ".join(problems))
