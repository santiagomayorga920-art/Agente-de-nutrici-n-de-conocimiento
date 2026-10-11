"""Tarjeta visual de la píldora (1080×1080 PNG) con Pillow: categoría, cifra clave, titular y
fuente sobre la imagen del artículo oscurecida o, si no hay, un degradado del color de la
categoría. Rápida (< 1 s) y sin servicios externos.
"""

import io
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
from PIL import Image, ImageDraw, ImageFont, ImageOps

from nutricion.domain.lesson import Pill

SIZE = 1080
MARGIN = 80
FONTS = Path(__file__).parent / "fonts"
MAX_IMAGE_BYTES = 8 * 1024 * 1024

# Color de acento por categoría (RGB)
ACCENTS = {
    "Negocios": (59, 130, 246),
    "Finanzas": (16, 185, 129),
    "Investigación": (168, 85, 247),
}
DEFAULT_ACCENT = (245, 158, 11)
BACKGROUND = (15, 23, 42)
WHITE = (248, 250, 252)
MUTED = (203, 213, 225)

MONTHS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(str(FONTS / name), size)


def render_card(
    pill: Pill,
    background: bytes | None = None,
    today: datetime | None = None,
    vivid: bool = False,
) -> bytes:
    """`vivid`: fondo ilustrado a propósito (no una foto cualquiera): se oscurece menos arriba
    para que se vea, y se mantiene oscuro abajo, donde va el texto."""
    accent = ACCENTS.get(pill.category, DEFAULT_ACCENT)
    image = _background(background, accent, top=40 if vivid else 120)
    draw = ImageDraw.Draw(image)
    width = SIZE - 2 * MARGIN

    # Cabecera: categoría (insignia) y marca
    label = (pill.category or "Noticia").upper()
    badge_font = _font(30, bold=True)
    pad_x, pad_y = 28, 14
    text_w = draw.textlength(label, font=badge_font)
    draw.rounded_rectangle(
        (MARGIN, MARGIN, MARGIN + text_w + 2 * pad_x, MARGIN + 30 + 2 * pad_y + 6),
        radius=30,
        fill=accent,
    )
    draw.text((MARGIN + pad_x, MARGIN + pad_y), label, font=badge_font, fill=WHITE)
    brand_font = _font(28, bold=True)
    brand = "NUTRICIÓN IA"
    draw.text(
        (SIZE - MARGIN - draw.textlength(brand, font=brand_font), MARGIN + pad_y + 2),
        brand,
        font=brand_font,
        fill=MUTED,
    )

    # Pie: fuente y fecha
    footer_font = _font(30)
    date = today or datetime.now()
    footer = f"{pill.source_name or 'Fuente'}  ·  {date.day} {MONTHS[date.month - 1]} {date.year}"
    footer = _ellipsize(draw, footer, footer_font, width)
    footer_y = SIZE - MARGIN - 30
    draw.text((MARGIN, footer_y), footer, font=footer_font, fill=MUTED)
    draw.rectangle((MARGIN, footer_y - 36, MARGIN + 120, footer_y - 30), fill=accent)

    # Titular, de abajo hacia arriba, reduciendo la letra hasta que quepa en 4 líneas
    headline_bottom = footer_y - 70
    # Sin cifra clave el titular ocupa el protagonismo (más grande y hasta 5 líneas)
    sizes, max_lines = ((68, 60, 54, 48, 42), 4) if pill.key_figure else ((88, 78, 68, 60, 52), 5)
    for size in sizes:
        font = _font(size, bold=True)
        lines = _wrap(draw, pill.headline, font, width)
        if len(lines) <= max_lines:
            break
    lines = lines[:max_lines]
    line_h = int(font.size * 1.22)
    y = headline_bottom - line_h * len(lines)
    headline_top = y
    for line in lines:
        draw.text((MARGIN, y), line, font=font, fill=WHITE)
        y += line_h

    # Cifra clave, en el espacio libre sobre el titular
    if pill.key_figure:
        figure_font = _fit(draw, pill.key_figure, width, sizes=(150, 130, 110, 90, 72))
        label_font = _font(36)
        label_lines = _wrap(draw, pill.key_figure_label, label_font, width)[:2]
        block_h = figure_font.size + 20 + len(label_lines) * 46
        top = MARGIN + 110
        free = headline_top - 50 - top
        y = top + max(0, (free - block_h) // 2)
        draw.text((MARGIN, y), pill.key_figure, font=figure_font, fill=accent)
        y += figure_font.size + 20
        for line in label_lines:
            draw.text((MARGIN, y), line, font=label_font, fill=MUTED)
            y += 46

    out = io.BytesIO()
    image.convert("RGB").save(out, format="PNG", optimize=True)
    return out.getvalue()


def fetch_background(url: str, http: httpx.Client | None = None) -> bytes | None:
    """Descarga la imagen del artículo; None si no se puede (la tarjeta usa el degradado)."""
    if not url:
        return None
    client = http or httpx.Client(timeout=10, follow_redirects=True)
    try:
        response = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200 or len(response.content) > MAX_IMAGE_BYTES:
            return None
        if not response.headers.get("content-type", "").startswith("image/"):
            return None
        return response.content
    except httpx.HTTPError:
        return None
    finally:
        if http is None:
            client.close()


def _background(data: bytes | None, accent: tuple[int, int, int], top: int = 120) -> Image.Image:
    base = None
    if data:
        try:
            base = ImageOps.fit(Image.open(io.BytesIO(data)).convert("RGB"), (SIZE, SIZE))
        except Exception:  # noqa: BLE001 - imagen corrupta o formato raro: degradado
            base = None
    if base is None:
        base = _gradient(BACKGROUND, tuple(int(c * 0.45) for c in accent))
    # Velo oscuro, más intenso abajo, para que el texto siempre se lea
    shade = Image.new("L", (1, SIZE))
    for y in range(SIZE):
        shade.putpixel((0, y), int(top + (245 - top) * (y / SIZE)))
    veil = Image.new("RGB", (SIZE, SIZE), BACKGROUND)
    return Image.composite(veil, base, shade.resize((SIZE, SIZE)))


def _gradient(top: tuple[int, int, int], bottom: tuple[int, ...]) -> Image.Image:
    column = Image.new("RGB", (1, SIZE))
    for y in range(SIZE):
        t = y / (SIZE - 1)
        column.putpixel(
            (0, y), tuple(int(a + (b - a) * t) for a, b in zip(top, bottom, strict=True))
        )
    return column.resize((SIZE, SIZE))


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in (text or "").split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _fit(draw: ImageDraw.ImageDraw, text: str, width: int, sizes: tuple[int, ...]):
    for size in sizes:
        font = _font(size, bold=True)
        if draw.textlength(text, font=font) <= width:
            return font
    return font


def _ellipsize(draw: ImageDraw.ImageDraw, text: str, font, width: int) -> str:
    if draw.textlength(text, font=font) <= width:
        return text
    while text and draw.textlength(text + "…", font=font) > width:
        text = text[:-1]
    return text + "…"


def build_card(pill: Pill, timezone: str = "UTC", background: bytes | None = None) -> bytes | None:
    """Tarjeta lista para enviar, o None si algo falla (se envía el formato anterior).
    `background` es la ilustración generada; sin ella se usa la foto del artículo."""
    try:
        today = datetime.now(ZoneInfo(timezone))
        if background:
            return render_card(pill, background, today, vivid=True)
        return render_card(pill, fetch_background(pill.image_url), today)
    except Exception:  # noqa: BLE001 - la tarjeta es un extra: nunca bloquea la píldora
        return None
