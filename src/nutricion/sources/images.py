"""Busca la imagen representativa de un artículo (etiqueta og:image) cuando el feed no trae una."""

import re

import httpx

_OG_IMAGE = re.compile(
    r"<meta[^>]+(?:property|name)=[\"'](?:og:image|twitter:image)[\"'][^>]*content=[\"']([^\"']+)",
    re.IGNORECASE,
)
_OG_IMAGE_REVERSED = re.compile(
    r"<meta[^>]+content=[\"']([^\"']+)[\"'][^>]*(?:property|name)=[\"'](?:og:image|twitter:image)",
    re.IGNORECASE,
)


def find_og_image(url: str, http: httpx.Client | None = None) -> str:
    """Devuelve la URL de la imagen o "" si no hay (nunca lanza excepción)."""
    client = http or httpx.Client(timeout=10, follow_redirects=True)
    try:
        response = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200 or "html" not in response.headers.get("content-type", ""):
            return ""
        page = response.text[:300_000]
    except httpx.HTTPError:
        return ""
    finally:
        if http is None:
            client.close()
    match = _OG_IMAGE.search(page) or _OG_IMAGE_REVERSED.search(page)
    image = match.group(1) if match else ""
    return image if image.startswith("https://") else ""
