import io

import httpx
from PIL import Image

from nutricion.domain.lesson import Pill
from nutricion.media.card import SIZE, build_card, fetch_background, render_card


def pill(**overrides) -> Pill:
    values = dict(
        headline="Startup de agentes de IA levanta 200 millones en una ronda Serie B",
        what_happened="",
        why_it_matters="",
        source_url="https://x",
        challenge="",
        source_name="Bloomberg",
        category="Finanzas",
        key_figure="200 M USD",
        key_figure_label="ronda Serie B liderada por a16z",
    )
    values.update(overrides)
    return Pill(**values)


def opened(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data))


def test_card_is_square_png():
    image = opened(render_card(pill()))
    assert image.format == "PNG" and image.size == (SIZE, SIZE)


def test_card_without_key_figure_and_very_long_headline():
    long = "Palabra " * 60 + "ñandú áéíóú"
    assert opened(render_card(pill(key_figure="", headline=long))).size == (SIZE, SIZE)


def test_card_uses_article_image_as_background():
    buffer = io.BytesIO()
    Image.new("RGB", (400, 300), (255, 0, 0)).save(buffer, format="JPEG")
    plain = opened(render_card(pill())).convert("RGB")
    with_photo = opened(render_card(pill(), buffer.getvalue())).convert("RGB")
    assert plain.getpixel((SIZE // 2, 300)) != with_photo.getpixel((SIZE // 2, 300))


def test_corrupt_background_falls_back_to_gradient():
    assert opened(render_card(pill(), b"no es una imagen")).size == (SIZE, SIZE)


def test_background_download_rejects_non_images():
    html = httpx.Client(
        transport=httpx.MockTransport(
            lambda r: httpx.Response(200, content=b"<html>", headers={"content-type": "text/html"})
        )
    )
    assert fetch_background("https://x", html) is None
    assert fetch_background("", html) is None


def test_build_card_never_raises():
    assert build_card(pill(image_url=""), "America/Bogota") is not None
    assert build_card(pill(image_url=""), "Zona/Inexistente") is None  # error: sin tarjeta
