import base64
import io

import httpx
import pytest
from PIL import Image

from nutricion.domain.lesson import Pill
from nutricion.media import card, illustration


def png() -> bytes:
    out = io.BytesIO()
    Image.new("RGB", (64, 64), (200, 50, 50)).save(out, "PNG")
    return out.getvalue()


def client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def pill(**overrides) -> Pill:
    fields = dict(
        headline="Costos de IA caen",
        what_happened="x",
        why_it_matters="y",
        source_url="https://e.com",
        challenge="¿?",
    )
    return Pill(**{**fields, **overrides})


def test_prompt_uses_scene_and_forbids_text():
    prompt = illustration.prompt_for(pill(image_prompt="Falling chips"))
    assert prompt.startswith("Falling chips. ") and "no text" in prompt
    assert "Costos de IA caen" in illustration.prompt_for(pill())


def test_cloudflare_is_used_when_configured():
    seen = []

    def handler(request):
        seen.append(request.url.host)
        assert request.headers["Authorization"] == "Bearer tok"
        image = base64.b64encode(png()).decode()
        return httpx.Response(200, json={"result": {"image": image}, "success": True})

    data = illustration.generate("p", "acc", "tok", client(handler))
    assert data == png() and seen == ["api.cloudflare.com"]


def test_falls_back_to_pollinations_without_credentials_or_on_failure():
    seen = []

    def handler(request):
        seen.append(request.url.host)
        if request.url.host == "api.cloudflare.com":
            return httpx.Response(429, json={"errors": [{"message": "límite"}]})
        assert request.url.params["nologo"] == "true"
        return httpx.Response(200, content=png(), headers={"content-type": "image/jpeg"})

    assert illustration.generate("p", "", "", client(handler)) == png()
    assert illustration.generate("p", "acc", "tok", client(handler)) == png()
    assert seen == ["image.pollinations.ai", "api.cloudflare.com", "image.pollinations.ai"]


def test_error_when_no_provider_answers():
    def handler(request):
        return httpx.Response(502, text="Bad Gateway", headers={"content-type": "text/html"})

    with pytest.raises(illustration.IllustrationError, match="Pollinations: HTTP 502"):
        illustration.generate("p", http=client(handler))


def test_card_uses_illustration_as_background():
    plain = card.build_card(pill())
    illustrated = card.build_card(pill(), background=png())
    assert illustrated and plain and illustrated != plain
    image = Image.open(io.BytesIO(illustrated)).convert("RGB")
    # Arriba se ve el rojo de la ilustración (velo ligero); abajo queda oscuro para el texto
    red, green, _ = image.getpixel((540, 5))
    assert red > green + 60
    assert sum(image.getpixel((540, 1075))) < 120
