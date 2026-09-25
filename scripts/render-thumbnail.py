#!/usr/bin/env python3
"""Landscape share thumbnail and square mark for the poetry book."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "assets" / "fonts" / "AbyssinicaSIL-R.ttf"
OUT = ROOT / "public" / "thumbnail.jpg"
ICON = ROOT / "app" / "apple-icon.png"

DEEP = (26, 14, 10)
BROWN = (43, 23, 16)
MID = (60, 36, 24)
WARM = (138, 90, 50)
GOLD = (196, 165, 116)
CREAM = (247, 241, 232)
INK = (43, 23, 16)


def gradient(size: tuple[int, int], a, b, c) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(h):
        for x in range(w):
            t = (x / w) * 0.55 + (y / h) * 0.45
            u = math.hypot((x / w) - 0.32, (y / h) - 0.42)
            glow = max(0.0, 1 - u / 0.85)
            r = int(a[0] * (1 - t) + b[0] * t + (c[0] - b[0]) * glow * 0.55)
            g = int(a[1] * (1 - t) + b[1] * t + (c[1] - b[1]) * glow * 0.55)
            bl = int(a[2] * (1 - t) + b[2] * t + (c[2] - b[2]) * glow * 0.55)
            px[x, y] = (min(255, r), min(255, g), min(255, bl))
    return img


def cubic(p0, p1, p2, p3, n=28) -> list[tuple[float, float]]:
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def emblem(base: Image.Image, cx: float, cy: float, scale: float) -> None:
    def m(x: float, y: float) -> tuple[float, float]:
        return (cx + (x - 450) * scale, cy + (y - 560) * scale)

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    ox, oy = m(450, 620)
    draw.ellipse([ox - 250 * scale, oy - 340 * scale, ox + 250 * scale, oy + 340 * scale], fill=BROWN + (150,))
    wing = []
    wing += cubic((250, 430), (340, 390), (400, 520), (450, 560))
    wing += cubic((450, 560), (500, 520), (560, 390), (650, 430))[1:]
    wing += cubic((650, 430), (600, 620), (520, 700), (450, 760))[1:]
    wing += cubic((450, 760), (380, 700), (300, 620), (250, 430))[1:]
    draw.polygon([m(x, y) for x, y in wing], fill=CREAM + (235,))
    vein = cubic((450, 470), (470, 560), (470, 680), (450, 760))
    vein += cubic((450, 760), (430, 680), (430, 560), (450, 470))[1:]
    draw.polygon([m(x, y) for x, y in vein], fill=BROWN + (230,))
    line = cubic((450, 310), (452, 420), (468, 560), (450, 880))
    draw.line([m(x, y) for x, y in line], fill=GOLD + (220,), width=max(2, int(3 * scale)))
    gx, gy = m(450, 430)
    r = 18 * scale
    draw.ellipse([gx - r, gy - r, gx + r, gy + r], fill=GOLD + (255,))
    base.paste(Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB"))


def text(draw: ImageDraw.ImageDraw, value: str, xy: tuple[int, int], size: int, fill, anchor: str = "lt") -> tuple[int, int]:
    font = ImageFont.truetype(str(FONT), size)
    draw.text(xy, value, font=font, fill=fill, anchor=anchor)
    box = draw.textbbox((0, 0), value, font=font)
    return box[2] - box[0], box[3] - box[1]


def thumbnail() -> None:
    w, h = 1200, 630
    img = gradient((w, h), DEEP, MID, (231, 199, 161))
    emblem(img, 330, 318, 0.78)
    draw = ImageDraw.Draw(img)
    # Open-book page on the right, so the title stays readable when the card is small.
    draw.polygon([(690, 0), (1200, 0), (1200, h), (650, h)], fill=CREAM)
    draw.polygon([(650, 0), (690, 0), (650, h), (612, h)], fill=GOLD)
    draw.line([(668, 36), (668, h - 36)], fill=(255, 248, 236), width=2)
    text(draw, "የግጥም መድብል  ·  ፩", (748, 118), 28, GOLD)
    text(draw, "አጫጭር", (748, 168), 92, INK)
    text(draw, "ግጥሞች", (748, 268), 92, INK)
    draw.line([(748, 400), (860, 400)], fill=GOLD, width=3)
    text(draw, "ሃያ ስምንት አጫጭር የፍቅር ግጥሞች", (748, 428), 28, (109, 83, 70))
    text(draw, "በ ገጣሚ ኪዳነ ማርያም ዘውዱ የተዘጋጀ", (748, 520), 24, INK)
    draw.rectangle([18, 18, w - 19, h - 19], outline=(247, 241, 232, ), width=2)
    grain = Image.effect_noise((w, h), 10).convert("L")
    img = Image.blend(img, Image.merge("RGB", (grain, grain, grain)), 0.05)
    img.save(OUT, quality=90, optimize=True)
    print("thumbnail", OUT, img.size)


def apple_icon() -> None:
    size = 180
    img = gradient((size, size), DEEP, BROWN, (231, 199, 161))
    emblem(img, 90, 96, 0.22)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([4, 4, size - 5, size - 5], radius=28, outline=CREAM, width=2)
    img.save(ICON, optimize=True)
    print("icon", ICON, img.size)


if __name__ == "__main__":
    thumbnail()
    apple_icon()
