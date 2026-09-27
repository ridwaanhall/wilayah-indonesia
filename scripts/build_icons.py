"""Build the site icons from one geometry: favicon.svg, favicon.ico and apple-touch-icon.png.

The mark is four stepped bars, one per administrative level (province, regency,
district, village), mirroring the explorer's cascade.

    uv run --with pillow python scripts/build_icons.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

STATIC = Path(__file__).resolve().parent.parent / "app" / "web" / "static"
GRID = 64
BACKGROUND = "#b4471e"
FOREGROUND = "#fff7f0"
CORNER = 14
BAR_HEIGHT, BAR_RADIUS, RIGHT = 8, 2, 54
BARS = [(10 + 8 * level, 10 + 12 * level) for level in range(4)]  # (x, y) per level


def svg() -> str:
    bars = "".join(
        f'<rect x="{x}" y="{y}" width="{RIGHT - x}" height="{BAR_HEIGHT}" rx="{BAR_RADIUS}"/>' for x, y in BARS
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {GRID} {GRID}">'
        f'<rect width="{GRID}" height="{GRID}" rx="{CORNER}" fill="{BACKGROUND}"/>'
        f'<g fill="{FOREGROUND}">{bars}</g></svg>\n'
    )


def raster(size: int, *, rounded: bool = True) -> Image.Image:
    scale = 1024 / GRID
    image = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, 1023, 1023), radius=CORNER * scale if rounded else 0, fill=BACKGROUND)
    for x, y in BARS:
        box = (x * scale, y * scale, RIGHT * scale, (y + BAR_HEIGHT) * scale)
        draw.rounded_rectangle(box, radius=BAR_RADIUS * scale, fill=FOREGROUND)
    return image.resize((size, size), Image.Resampling.LANCZOS)


if __name__ == "__main__":
    (STATIC / "favicon.svg").write_text(svg(), encoding="utf-8")
    raster(256).save(STATIC / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    # iOS applies its own mask, so the touch icon is a full square.
    raster(180, rounded=False).save(STATIC / "apple-touch-icon.png")
