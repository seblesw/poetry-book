#!/usr/bin/env python3
"""Paste cut-paper people onto the original plates.

The first-edition plate stays the ground. Each person is gouache and
torn paper: a kemis or netela, a tibeb hem, a face built from a few
ink strokes. Where a figure crosses the old drawing, the old drawing
is laid back on top, so the two pictures share the page.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / ".cache" / "old-plates"
OUT = ROOT / "public" / "plates"
W, H = 1200, 1600

SKIN = [(168, 112, 74), (138, 84, 56), (196, 146, 108), (112, 70, 48), (154, 98, 68)]
HAIR = [(32, 20, 14), (48, 30, 20), (22, 16, 12), (62, 36, 22)]
INK = (48, 28, 20)
GOLD = (196, 158, 96)
CREAM = (244, 236, 224)
ROSE = (158, 78, 68)

# ground, fold, tibeb bands
CLOTH = [
    ((236, 228, 214), (214, 204, 188), [(168, 52, 46), (42, 96, 64), (196, 154, 72)]),
    ((124, 46, 52), (96, 32, 38), [(236, 220, 196), (196, 154, 72)]),
    ((46, 62, 98), (32, 44, 74), [(232, 220, 196), (196, 154, 72), (168, 52, 46)]),
    ((176, 108, 52), (142, 82, 36), [(48, 28, 20), (236, 220, 196)]),
    ((52, 86, 68), (36, 64, 50), [(236, 220, 196), (168, 52, 46), (196, 154, 72)]),
    ((92, 48, 62), (70, 34, 46), [(236, 220, 196), (42, 96, 64)]),
]


def blob(cx: float, cy: float, rx: float, ry: float, seed: int, n: int = 36) -> list[tuple[float, float]]:
    rnd = random.Random(seed)
    points = []
    for i in range(n):
        angle = math.tau * i / n
        jitter = 1 + rnd.uniform(-0.045, 0.05)
        points.append((cx + math.cos(angle) * rx * jitter, cy + math.sin(angle) * ry * jitter))
    return points


def paste_poly(base: Image.Image, points: list[tuple[float, float]], fill) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).polygon(points, fill=fill)
    base.alpha_composite(layer)


def limb(base: Image.Image, a: tuple[float, float], b: tuple[float, float], width: float, fill) -> None:
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy) or 1
    px, py = -dy / length * width, dx / length * width
    paste_poly(
        base,
        [(a[0] + px, a[1] + py), (a[0] - px, a[1] - py), (b[0] - px, b[1] - py), (b[0] + px, b[1] + py)],
        fill,
    )


def cloth_body(plate: Image.Image, points: list[tuple[float, float]], cloth_i: int, seed: int) -> Image.Image:
    ground, _fold, bands = CLOTH[cloth_i % len(CLOTH)]
    mask = Image.new("L", plate.size, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    mask = mask.filter(ImageFilter.MaxFilter(3))
    faded = ImageEnhance.Color(plate).enhance(0.72)
    faded = ImageEnhance.Brightness(faded).enhance(1.04)
    wash = Image.new("RGB", plate.size, ground)
    woven = Image.blend(faded, wash, 0.62)
    layer = Image.new("RGBA", plate.size, (0, 0, 0, 0))
    layer.paste(woven.convert("RGBA"), mask=mask)
    draw = ImageDraw.Draw(layer)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    left, right, hem = min(xs), max(xs), max(ys)
    rnd = random.Random(seed)
    y = hem - 22
    for band in bands:
        draw.line([(left + 8, y), (right - 8, y)], fill=band + (210,), width=7)
        y -= 12
    # A short run of tibeb diamonds, shifted so each garment is its own cloth.
    stitch = GOLD if cloth_i % 2 == 0 else CREAM
    for i in range(5):
        cx = left + (right - left) * (0.28 + 0.11 * i)
        cy = hem - 78 - (i % 2) * 10
        d = 7 + rnd.randint(0, 2)
        draw.polygon([(cx, cy - d), (cx + d, cy), (cx, cy + d), (cx - d, cy)], outline=stitch + (180,))
    layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", layer.size, 0), mask))
    return layer


def head_guard(mask: Image.Image, people: list) -> Image.Image:
    draw = ImageDraw.Draw(mask)
    for person in people:
        cx, foot, scale, _facing, pose, *_rest = person
        s = scale
        chest = foot - ((460 if pose == "stand" else 320) * s)
        hy = chest - 145 * s
        draw.ellipse([cx - 92 * s, hy - 100 * s, cx + 96 * s, hy + 108 * s], fill=0)
    return mask


def motif_mask(plate: Image.Image) -> Image.Image:
    blur = plate.filter(ImageFilter.GaussianBlur(26))
    diff = ImageChops.difference(plate, blur).convert("L")
    mask = diff.point(lambda p: 255 if p > 16 else 0)
    return mask.filter(ImageFilter.MaxFilter(3))


def hair_back(base: Image.Image, cx: float, hy: float, s: float, kind: str, color, seed: int) -> None:
    if kind == "afro":
        paste_poly(base, blob(cx, hy - 8 * s, 132 * s, 118 * s, seed, 28), color + (255,))
    elif kind == "crop":
        paste_poly(base, blob(cx, hy - 36 * s, 108 * s, 64 * s, seed, 22), color + (255,))
    elif kind == "bun":
        paste_poly(base, blob(cx + 36 * s, hy - 78 * s, 46 * s, 42 * s, seed, 18), color + (255,))
        paste_poly(base, blob(cx, hy - 28 * s, 100 * s, 58 * s, seed + 1, 20), color + (255,))
    elif kind == "braids":
        paste_poly(base, blob(cx, hy - 30 * s, 104 * s, 62 * s, seed, 20), color + (255,))
        draw = ImageDraw.Draw(base)
        for side in (-1, 1):
            for i in range(2):
                x0 = cx + side * (52 + i * 14) * s
                draw.line(
                    [(x0, hy - 4 * s), (x0 + side * 6 * s, hy + 78 * s), (x0 + side * 2 * s, hy + 150 * s)],
                    fill=color + (255,),
                    width=5,
                )
    # wrap is painted after the face


def hair_front(base: Image.Image, cx: float, hy: float, s: float, kind: str, color, seed: int, facing: str) -> None:
    draw = ImageDraw.Draw(base)
    if kind == "wrap":
        paste_poly(base, blob(cx, hy - 48 * s, 128 * s, 78 * s, seed, 24), (236, 226, 210, 255))
        drape_x = cx + (70 * s if facing != "right" else -70 * s)
        paste_poly(
            base,
            [
                (cx - 90 * s, hy - 20 * s),
                (cx + 90 * s, hy - 28 * s),
                (drape_x, hy + 120 * s),
                (drape_x - 36 * s, hy + 110 * s),
            ],
            (236, 226, 210, 255),
        )
        draw.line([(cx - 80 * s, hy - 8 * s), (cx + 80 * s, hy - 16 * s)], fill=GOLD + (230,), width=6)
        draw.line([(cx - 80 * s, hy + 2 * s), (cx + 78 * s, hy - 4 * s)], fill=(168, 52, 46, 220), width=3)


def features(draw: ImageDraw.ImageDraw, cx: float, hy: float, s: float, expr: str, look: float) -> None:
    eye_y = hy + (16 * s if expr == "down" else 4 * s)
    shift = look * 8 * s
    for side in (-1, 1):
        ex = cx + side * 26 * s + shift
        if expr == "closed":
            draw.arc([ex - 12 * s, eye_y - 4 * s, ex + 12 * s, eye_y + 10 * s], 200, 345, fill=INK, width=3)
        else:
            draw.arc([ex - 13 * s, eye_y - 6 * s, ex + 13 * s, eye_y + 8 * s], 205, 345, fill=INK, width=3)
            px = ex + look * 3 * s
            draw.ellipse([px - 2.4 * s, eye_y - 1 * s, px + 2.4 * s, eye_y + 4 * s], fill=INK)
        brow_y = eye_y - 14 * s
        tilt = -4 * s if expr in {"down", "closed"} else 0
        draw.line([(ex - 12 * s, brow_y + tilt), (ex + 11 * s, brow_y - tilt)], fill=INK, width=2)
    draw.arc([cx - 4 * s + shift * 0.2, hy + 16 * s, cx + 14 * s + shift * 0.2, hy + 40 * s], 250, 20, fill=tuple(max(0, c - 28) for c in (140, 90, 64)), width=2)
    mouth = [cx - 16 * s + shift * 0.15, hy + 48 * s, cx + 16 * s + shift * 0.15, hy + 66 * s]
    if expr == "open":
        draw.arc(mouth, 15, 165, fill=ROSE, width=3)
    elif expr == "flat" or expr == "down":
        draw.line([(mouth[0], hy + 56 * s), (mouth[2], hy + 58 * s)], fill=ROSE, width=3)
    else:
        draw.arc(mouth, 12, 168, fill=ROSE, width=3)


def profile_head(base: Image.Image, cx: float, hy: float, s: float, skin, facing: str, expr: str) -> None:
    sign = 1 if facing == "right" else -1
    raw = [
        (0.02, 0.28), (0.16, 0.06), (0.40, 0.00), (0.56, 0.08),
        (0.62, 0.24), (0.70, 0.36), (0.58, 0.44), (0.64, 0.52),
        (0.48, 0.70), (0.26, 0.86), (0.00, 0.58),
    ]
    pts = [(cx + sign * (x - 0.28) * 210 * s, hy + (y - 0.35) * 230 * s) for x, y in raw]
    paste_poly(base, pts, skin + (255,))
    draw = ImageDraw.Draw(base)
    eye_x = cx + sign * 28 * s
    eye_y = hy - 8 * s
    if expr == "closed":
        draw.arc([eye_x - 10 * s, eye_y - 4 * s, eye_x + 8 * s, eye_y + 8 * s], 200, 340, fill=INK, width=3)
    else:
        draw.ellipse([eye_x - 3 * s, eye_y - 3 * s, eye_x + 3 * s, eye_y + 3 * s], fill=INK)
    lip_x = cx + sign * 62 * s
    draw.line([(lip_x, hy + 28 * s), (lip_x - sign * 12 * s, hy + 34 * s)], fill=ROSE, width=3)


def paint_prop(draw: ImageDraw.ImageDraw, kind: str, x: float, y: float, s: float) -> None:
    if kind == "phone":
        draw.rounded_rectangle([x - 13 * s, y - 24 * s, x + 13 * s, y + 24 * s], 4, fill=(28, 22, 18), outline=GOLD, width=2)
        draw.rectangle([x - 8 * s, y - 16 * s, x + 8 * s, y + 10 * s], fill=(232, 196, 140))
    elif kind == "flower":
        for i in range(6):
            a = math.tau * i / 6
            draw.ellipse(
                [x + math.cos(a) * 12 * s - 7 * s, y + math.sin(a) * 12 * s - 7 * s, x + math.cos(a) * 12 * s + 7 * s, y + math.sin(a) * 12 * s + 7 * s],
                fill=(176, 64, 58),
            )
        draw.ellipse([x - 5 * s, y - 5 * s, x + 5 * s, y + 5 * s], fill=GOLD)
        draw.line([(x, y + 6 * s), (x - 4 * s, y + 54 * s)], fill=(46, 90, 52), width=3)
    elif kind == "mask":
        draw.polygon(blob(x, y, 36 * s, 46 * s, 21, 26), fill=CREAM)
        draw.ellipse([x - 16 * s, y - 10 * s, x - 4 * s, y + 4 * s], fill=INK)
        draw.ellipse([x + 6 * s, y - 10 * s, x + 18 * s, y + 4 * s], fill=INK)
        draw.arc([x - 12 * s, y + 8 * s, x + 14 * s, y + 24 * s], 20, 160, fill=INK, width=2)
    elif kind == "coin":
        for i, dx in enumerate((-10, 4, 16)):
            draw.ellipse([x + dx * s - 7 * s, y + i * 3 * s, x + dx * s + 7 * s, y + i * 3 * s + 14 * s], fill=GOLD, outline=INK)
    elif kind == "book":
        draw.polygon([(x - 26 * s, y - 6 * s), (x + 2 * s, y - 16 * s), (x + 30 * s, y - 2 * s), (x + 2 * s, y + 14 * s)], fill=CREAM, outline=INK)
        draw.line([(x + 2 * s, y - 14 * s), (x + 2 * s, y + 12 * s)], fill=GOLD, width=2)
    elif kind == "cup":
        draw.pieslice([x - 14 * s, y - 6 * s, x + 14 * s, y + 18 * s], 0, 180, fill=(92, 58, 40))
        draw.arc([x - 16 * s, y - 12 * s, x + 16 * s, y + 16 * s], 200, 340, fill=CREAM, width=3)
        draw.arc([x + 10 * s, y - 2 * s, x + 26 * s, y + 16 * s], 280, 80, fill=CREAM, width=3)
    elif kind == "jebena":
        draw.polygon([(x, y - 34 * s), (x + 18 * s, y + 16 * s), (x - 10 * s, y + 16 * s)], fill=(92, 42, 32))
        draw.ellipse([x - 16 * s, y + 6 * s, x + 24 * s, y + 32 * s], fill=(72, 32, 26))
        draw.line([(x + 2 * s, y - 8 * s), (x + 28 * s, y - 24 * s)], fill=(72, 32, 26), width=4)
        draw.ellipse([x + 22 * s, y - 30 * s, x + 34 * s, y - 18 * s], outline=(72, 32, 26), width=3)
    elif kind == "bag":
        draw.rounded_rectangle([x - 20 * s, y - 14 * s, x + 20 * s, y + 26 * s], 3, fill=(62, 44, 32), outline=GOLD, width=2)
        draw.arc([x - 14 * s, y - 26 * s, x + 14 * s, y - 2 * s], 200, 340, fill=GOLD, width=3)
    elif kind == "bulb":
        draw.ellipse([x - 14 * s, y - 20 * s, x + 14 * s, y + 8 * s], fill=(244, 214, 150), outline=GOLD)
        draw.rectangle([x - 6 * s, y + 6 * s, x + 6 * s, y + 16 * s], fill=INK)
    elif kind == "mirror":
        draw.rounded_rectangle([x - 18 * s, y - 28 * s, x + 18 * s, y + 28 * s], 8, outline=GOLD, width=4)
        draw.ellipse([x - 8 * s, y - 10 * s, x + 8 * s, y + 12 * s], fill=(232, 214, 196))


def paint_person(
    base: Image.Image,
    plate: Image.Image,
    cx: float,
    foot: float,
    scale: float,
    facing: str,
    pose: str,
    skin_i: int,
    hair: str,
    cloth_i: int,
    expr: str,
    prop: str | None,
    seed: int,
) -> None:
    s = scale
    skin = SKIN[skin_i % len(SKIN)]
    hair_c = HAIR[seed % len(HAIR)]
    sign = 0 if facing == "front" else (1 if facing == "right" else -1)
    chest = foot - (460 * s if pose == "stand" else 320 * s)
    hy = chest - 145 * s
    # Paper shadow, offset like a scrap that was set down by hand.
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([cx - 90 * s, foot - 16 * s, cx + 100 * s, foot + 22 * s], fill=(40, 24, 16, 80))
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6)))

    if pose == "stand":
        parts = [[
            (cx - 72 * s, chest + 8 * s),
            (cx + 78 * s, chest - 4 * s),
            (cx + 108 * s, chest + 170 * s),
            (cx + 156 * s, foot),
            (cx - 164 * s, foot - 12 * s),
            (cx - 96 * s, chest + 180 * s),
        ]]
    else:
        parts = [
            [
                (cx - 74 * s, chest + 4 * s),
                (cx + 78 * s, chest - 8 * s),
                (cx + 90 * s, chest + 148 * s),
                (cx - 86 * s, chest + 156 * s),
            ],
            [
                (cx - 110 * s, chest + 132 * s),
                (cx + 30 * s, chest + 118 * s),
                (cx + 200 * s, chest + 148 * s),
                (cx + 176 * s, chest + 198 * s),
                (cx - 80 * s, chest + 188 * s),
            ],
            [
                (cx + 150 * s, chest + 170 * s),
                (cx + 188 * s, chest + 156 * s),
                (cx + 168 * s, foot),
                (cx + 124 * s, foot - 6 * s),
            ],
        ]
    body = parts[0]
    _ground, fold, _bands = CLOTH[cloth_i % len(CLOTH)]
    for part in parts:
        paste_poly(base, [(x - 8, y + 10) for x, y in part], CREAM + (200,))
    paste_poly(base, [body[0], body[1], (cx + 8 * s, chest + 150 * s), (cx - 48 * s, chest + 156 * s)], fold + (255,))
    for part in parts:
        base.alpha_composite(cloth_body(plate, part, cloth_i, seed))
        ImageDraw.Draw(base).line(part + [part[0]], fill=CREAM + (230,), width=3)

    # Shawl over the far shoulder. White netela, one colored edge.
    if cloth_i % 2 == 0:
        shawl = [
            (cx - 80 * s, chest + 4 * s),
            (cx + 20 * s, chest - 20 * s),
            (cx + 70 * s, chest + 80 * s),
            (cx - 20 * s, chest + 150 * s),
        ]
        paste_poly(base, shawl, (244, 238, 228, 235))
        ImageDraw.Draw(base).line([shawl[0], shawl[3]], fill=(168, 52, 46, 220), width=4)

    neck = [
        (cx - 22 * s, hy + 78 * s),
        (cx + 22 * s, hy + 74 * s),
        (cx + 30 * s, chest + 16 * s),
        (cx - 28 * s, chest + 18 * s),
    ]
    paste_poly(base, neck, skin + (255,))

    near = sign if sign else 1
    shoulder = (cx + near * 62 * s, chest + 16 * s)
    elbow = (cx + near * 110 * s, chest + 90 * s)
    hand = (cx + near * 132 * s, chest + 36 * s if prop in {"mask", "flower", "bulb"} else chest + 70 * s)
    if prop in {"phone", "cup", "book", "mirror"}:
        hand = (cx + near * 78 * s, chest + 48 * s)
    limb(base, (cx - near * 58 * s, chest + 20 * s), (cx - near * 90 * s, chest + 120 * s), 11 * s, skin + (255,))
    limb(base, shoulder, elbow, 12 * s, skin + (255,))
    limb(base, elbow, hand, 10 * s, skin + (255,))
    paste_poly(base, blob(hand[0], hand[1], 16 * s, 14 * s, seed + 3, 14), skin + (255,))

    hair_back(base, cx + sign * 8 * s, hy, s, hair, hair_c, seed)
    if facing == "front":
        paste_poly(base, blob(cx, hy + 10 * s, 78 * s, 96 * s, seed + 5, 32), skin + (255,))
        # A paper highlight and a little warmth in the cheek. Still flat gouache.
        paste_poly(base, blob(cx - 18 * s, hy - 16 * s, 28 * s, 22 * s, seed + 8, 12), tuple(min(255, c + 24) for c in skin) + (140,))
        draw = ImageDraw.Draw(base)
        draw.ellipse([cx - 46 * s, hy + 28 * s, cx - 24 * s, hy + 44 * s], fill=(186, 110, 96, 70))
        draw.ellipse([cx + 24 * s, hy + 30 * s, cx + 44 * s, hy + 44 * s], fill=(186, 110, 96, 70))
        ear_x = cx - 70 * s
        draw.ellipse([ear_x - 10 * s, hy + 8 * s, ear_x + 12 * s, hy + 36 * s], fill=tuple(max(0, c - 16) for c in skin) + (255,))
        features(draw, cx, hy, s, expr, 0.6 if sign == 0 else sign)
        if seed % 3 == 0:
            draw.ellipse([ear_x - 3 * s, hy + 28 * s, ear_x + 5 * s, hy + 36 * s], outline=GOLD, width=2)
    else:
        profile_head(base, cx, hy, s, skin, facing, expr)
    hair_front(base, cx, hy, s, hair, hair_c, seed, facing)

    if prop:
        paint_prop(ImageDraw.Draw(base), prop, hand[0] + near * 8 * s, hand[1] - 8 * s, s * 1.15)


def rain(base: Image.Image) -> None:
    draw = ImageDraw.Draw(base)
    rnd = random.Random(15)
    for _ in range(70):
        x, y = rnd.randint(40, W - 40), rnd.randint(40, H - 40)
        draw.line([(x, y), (x - 14, y + 36)], fill=(226, 232, 236, 110), width=2)


def fork(base: Image.Image, cx: float) -> None:
    draw = ImageDraw.Draw(base)
    draw.line([(cx, 1320), (cx, 1080)], fill=CREAM, width=8)
    draw.line([(cx, 1080), (cx - 220, 860)], fill=GOLD, width=8)
    draw.line([(cx, 1080), (cx + 230, 840)], fill=CREAM, width=8)


# cx, foot, scale, facing, pose, skin, hair, cloth, expr, prop, lean
People = list[tuple]
SCENES: dict[str, dict] = {
    "cover": {"people": [(390, 1500, 0.78, "right", "stand", 1, "wrap", 0, "soft", "book", -4)]},
    "end": {"people": [(760, 1480, 0.74, "left", "stand", 3, "bun", 2, "closed", "book", 3)], "quiet": True},
    "01": {"people": [(820, 1540, 0.92, "left", "sit", 0, "crop", 4, "down", None, -2)]},
    "02": {"people": [(640, 1500, 0.8, "front", "stand", 2, "afro", 1, "flat", "phone", 2)]},
    "03": {"people": [(300, 1500, 0.62, "right", "stand", 1, "braids", 0, "down", None, -3), (900, 1510, 0.6, "left", "stand", 4, "crop", 5, "down", None, 3)]},
    "04": {"people": [(700, 1480, 0.78, "left", "stand", 3, "wrap", 2, "closed", None, -2)]},
    "05": {"people": [(520, 1490, 0.8, "right", "stand", 0, "bun", 3, "down", None, 2)]},
    "06": {"people": [(680, 1500, 0.82, "front", "stand", 1, "afro", 0, "open", None, -1)]},
    "07": {"people": [(640, 1490, 0.78, "front", "stand", 4, "braids", 5, "soft", "flower", 3)]},
    "08": {"people": [(760, 1500, 0.76, "left", "stand", 2, "crop", 1, "flat", None, -3)]},
    "09": {"people": [(340, 1510, 0.64, "right", "stand", 0, "afro", 4, "soft", None, -2), (880, 1490, 0.66, "left", "stand", 3, "braids", 0, "soft", None, 2)]},
    "10": {"people": [(620, 1490, 0.78, "front", "stand", 1, "crop", 3, "open", "phone", 1)]},
    "11": {"people": [(600, 1500, 0.8, "front", "stand", 4, "wrap", 2, "down", None, -2)]},
    "12": {"people": [(600, 1470, 0.7, "front", "stand", 2, "afro", 0, "soft", None, 0), (300, 1520, 0.52, "right", "stand", 0, "crop", 5, "down", None, -4), (920, 1520, 0.52, "left", "stand", 3, "bun", 1, "down", None, 4)]},
    "13": {"people": [(860, 1340, 0.98, "left", "stand", 3, "wrap", 0, "soft", "jebena", 1)]},
    "14": {"people": [(640, 1490, 0.78, "front", "stand", 2, "crop", 1, "down", None, -2)]},
    "15": {"people": [(640, 1580, 0.74, "front", "sit", 0, "wrap", 2, "closed", None, 1)], "rain": True},
    "16": {"people": [(680, 1470, 0.86, "right", "stand", 2, "crop", 3, "flat", None, 2)]},
    "17": {"people": [(300, 1500, 0.7, "right", "stand", 1, "bun", 4, "open", "bulb", -3)]},
    "18": {"people": [(780, 1490, 0.78, "left", "stand", 3, "afro", 5, "flat", "bag", 2)]},
    "19": {"people": [(600, 1500, 0.78, "front", "sit", 0, "braids", 1, "down", None, -1)]},
    "20": {"people": [(700, 1460, 0.72, "front", "sit", 4, "crop", 3, "closed", "cup", 2)]},
    "21": {"people": [(460, 1500, 0.8, "right", "stand", 1, "afro", 5, "flat", "mask", -2)]},
    "22": {"people": [(640, 1490, 0.8, "right", "stand", 2, "crop", 4, "flat", "bag", 3)]},
    "23": {"people": [(480, 1490, 0.78, "right", "stand", 3, "wrap", 0, "soft", "mirror", -2)]},
    "24": {"people": [(340, 1520, 0.7, "right", "stand", 0, "crop", 3, "open", "coin", -2), (900, 1540, 0.64, "left", "stand", 4, "braids", 2, "flat", None, 3)]},
    "25": {"people": [(360, 1500, 0.78, "right", "stand", 2, "afro", 1, "down", None, -2)]},
    "26": {"people": [(640, 1460, 0.74, "front", "sit", 1, "bun", 0, "soft", "cup", -2)]},
    "27": {"people": [(400, 1500, 0.66, "front", "stand", 0, "crop", 2, "down", "phone", -2), (860, 1490, 0.64, "left", "stand", 3, "wrap", 0, "soft", None, 2)]},
    "28": {"people": [(400, 1500, 0.66, "right", "stand", 4, "braids", 5, "soft", "book", -3), (840, 1490, 0.66, "left", "stand", 1, "afro", 4, "open", None, 3)]},
}


def compose(key: str, spec: dict) -> None:
    plate = Image.open(OLD / f"{key}.jpg").convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    ground = plate if not spec.get("quiet") else ImageEnhance.Brightness(plate).enhance(1.04)
    base = ground.convert("RGBA")
    for index, person in enumerate(spec["people"]):
        cx, foot, scale, facing, pose, skin_i, hair, cloth_i, expr, prop, lean = person
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        paint_person(layer, plate, cx, foot, scale, facing, pose, skin_i, hair, cloth_i, expr, prop, seed=index * 19 + sum(ord(c) for c in key))
        if lean:
            layer = layer.rotate(lean, resample=Image.Resampling.BICUBIC, center=(cx, foot - 280))
        base.alpha_composite(layer)
    # The original drawing sits in front of the paper figure wherever they meet.
    base = Image.composite(plate.convert("RGBA"), base, head_guard(motif_mask(plate), spec["people"]))
    if spec.get("rain"):
        rain(base)
    if spec.get("fork"):
        fork(base, spec["fork"])
    grain = Image.effect_noise((W, H), 14).convert("L")
    base = Image.alpha_composite(base, Image.merge("RGBA", (grain, grain, grain, Image.new("L", (W, H), 22))))
    rgb = base.convert("RGB")
    rgb.save(OUT / f"{key}.jpg", quality=86, optimize=True)
    print(key, (OUT / f"{key}.jpg").stat().st_size)


def main() -> None:
    for key, spec in SCENES.items():
        compose(key, spec)


if __name__ == "__main__":
    main()
