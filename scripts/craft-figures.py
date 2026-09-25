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
    elif kind == "long":
        paste_poly(base, blob(cx, hy - 24 * s, 108 * s, 70 * s, seed, 22), color + (255,))
        paste_poly(base, [(cx - 78 * s, hy), (cx - 40 * s, hy - 10 * s), (cx - 28 * s, hy + 210 * s), (cx - 86 * s, hy + 200 * s)], color + (255,))
        paste_poly(base, [(cx + 40 * s, hy - 10 * s), (cx + 78 * s, hy), (cx + 86 * s, hy + 200 * s), (cx + 28 * s, hy + 210 * s)], color + (255,))
    elif kind in {"beard", "mustache", "fade"}:
        paste_poly(base, blob(cx, hy - 34 * s, 100 * s, 52 * s, seed, 20), color + (255,))
    # bald is bare. wrap is painted after the face.


def hair_front(base: Image.Image, cx: float, hy: float, s: float, kind: str, color, seed: int, facing: str) -> None:
    draw = ImageDraw.Draw(base)
    if kind == "wrap":
        paste_poly(base, blob(cx, hy - 72 * s, 108 * s, 46 * s, seed, 22), (236, 226, 210, 255))
        draw.line([(cx - 70 * s, hy - 78 * s), (cx + 70 * s, hy - 84 * s)], fill=GOLD + (230,), width=5)
        draw.line([(cx - 68 * s, hy - 66 * s), (cx + 68 * s, hy - 72 * s)], fill=(168, 52, 46, 220), width=3)
        if facing != "front":
            drape_x = cx + (78 * s if facing == "left" else -78 * s)
            paste_poly(
                base,
                [(cx, hy - 60 * s), (cx + (20 * s if facing == "left" else -20 * s), hy - 50 * s), (drape_x, hy + 90 * s), (drape_x - 28 * s, hy + 80 * s)],
                (236, 226, 210, 255),
            )


def features(draw: ImageDraw.ImageDraw, cx: float, hy: float, s: float, expr: str, look: float) -> None:
    eye_y = hy + (18 * s if expr in {"down", "shy"} else 2 * s)
    shift = look * 10 * s
    for side in (-1, 1):
        ex = cx + side * 28 * s + shift
        if expr == "closed":
            draw.arc([ex - 14 * s, eye_y - 4 * s, ex + 14 * s, eye_y + 12 * s], 200, 345, fill=INK, width=3)
        elif expr == "shy":
            draw.arc([ex - 13 * s, eye_y - 2 * s, ex + 13 * s, eye_y + 10 * s], 200, 345, fill=INK, width=3)
        else:
            draw.arc([ex - 14 * s, eye_y - 8 * s, ex + 14 * s, eye_y + 10 * s], 200, 350, fill=INK, width=3)
            px = ex + look * 4 * s
            draw.ellipse([px - 3 * s, eye_y - 1 * s, px + 3 * s, eye_y + 5 * s], fill=INK)
        brow_y = eye_y - 16 * s
        if expr == "worry":
            draw.line([(ex - 14 * s, brow_y - side * 5 * s), (ex + 14 * s, brow_y + side * 6 * s)], fill=INK, width=3)
        elif expr in {"down", "closed", "shy"}:
            draw.line([(ex - 14 * s, brow_y + 3 * s), (ex + 13 * s, brow_y - 2 * s)], fill=INK, width=3)
        else:
            draw.line([(ex - 14 * s, brow_y), (ex + 14 * s, brow_y - 1 * s)], fill=INK, width=3)
    nose = tuple(max(0, c - 36) for c in (150, 96, 68))
    draw.line([(cx + shift * 0.2, hy + 18 * s), (cx + 8 * s + shift * 0.15, hy + 40 * s)], fill=nose, width=2)
    mouth = [cx - 18 * s + shift * 0.15, hy + 46 * s, cx + 18 * s + shift * 0.15, hy + 68 * s]
    if expr in {"open", "smile"}:
        draw.arc(mouth, 15, 165, fill=ROSE, width=4)
    elif expr in {"flat", "down", "worry", "shy"}:
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


def solid(base: Image.Image, points: list[tuple[float, float]], fill) -> None:
    paste_poly(base, points, fill + (255,))
    ImageDraw.Draw(base).line(points + [points[0]], fill=INK + (210,), width=2)


def hem(draw: ImageDraw.ImageDraw, left: float, right: float, y: float, bands) -> None:
    for band in bands:
        draw.line([(left, y), (right, y)], fill=band + (230,), width=7)
        y -= 11


def front_head(base: Image.Image, cx: float, hy: float, s: float, skin, build: str) -> None:
    if build == "woman":
        pts = [
            (cx - 62 * s, hy - 10 * s), (cx - 48 * s, hy - 78 * s), (cx, hy - 96 * s),
            (cx + 50 * s, hy - 76 * s), (cx + 64 * s, hy - 8 * s), (cx + 36 * s, hy + 62 * s),
            (cx, hy + 84 * s), (cx - 34 * s, hy + 64 * s),
        ]
    elif build == "elder":
        pts = [
            (cx - 70 * s, hy), (cx - 58 * s, hy - 70 * s), (cx, hy - 86 * s),
            (cx + 60 * s, hy - 68 * s), (cx + 72 * s, hy + 4 * s), (cx + 46 * s, hy + 78 * s),
            (cx, hy + 96 * s), (cx - 44 * s, hy + 76 * s),
        ]
    else:
        pts = [
            (cx - 72 * s, hy - 4 * s), (cx - 64 * s, hy - 72 * s), (cx, hy - 88 * s),
            (cx + 66 * s, hy - 70 * s), (cx + 76 * s, hy), (cx + 58 * s, hy + 70 * s),
            (cx + 16 * s, hy + 92 * s), (cx - 18 * s, hy + 90 * s), (cx - 54 * s, hy + 68 * s),
        ]
    paste_poly(base, pts, skin + (255,))


def beard(base: Image.Image, cx: float, hy: float, s: float) -> None:
    paste_poly(
        base,
        [(cx - 26 * s, hy + 70 * s), (cx + 30 * s, hy + 72 * s), (cx + 14 * s, hy + 108 * s), (cx, hy + 116 * s), (cx - 12 * s, hy + 104 * s)],
        (42, 28, 20, 255),
    )


def hand(base: Image.Image, x: float, y: float, s: float, skin) -> None:
    paste_poly(base, blob(x, y, 16 * s, 13 * s, int(x + y) % 90, 12), skin + (255,))


def shoe(base: Image.Image, x: float, y: float, s: float, sign: float = 1) -> None:
    paste_poly(base, [(x - 16 * s, y - 8 * s), (x + 22 * s * sign, y - 10 * s), (x + 28 * s * sign, y + 8 * s), (x - 14 * s, y + 8 * s)], (32, 24, 20, 255))


def arms(base: Image.Image, cx: float, shoulder: float, hip: float, hy: float, s: float, skin, gesture: str, near: float) -> tuple[float, float]:
    left = (cx - 72 * s, shoulder + 16 * s)
    right = (cx + 74 * s, shoulder + 12 * s)
    hold = (cx + near * 20 * s, shoulder + 90 * s)
    if gesture == "think":
        limb(base, right, (cx + 40 * s, hy + 36 * s), 11 * s, skin + (255,))
        hand(base, cx + 46 * s, hy + 30 * s, s, skin)
        limb(base, left, (cx - 96 * s, hip + 20 * s), 11 * s, skin + (255,))
        hand(base, cx - 96 * s, hip + 28 * s, s, skin)
        hold = (cx + 46 * s, hy + 30 * s)
    elif gesture == "reach":
        hold = (cx + near * 168 * s, shoulder + 10 * s)
        limb(base, right if near > 0 else left, hold, 12 * s, skin + (255,))
        hand(base, hold[0], hold[1], s, skin)
        other = left if near > 0 else right
        limb(base, other, (other[0] - near * 20 * s, hip + 36 * s), 11 * s, skin + (255,))
    elif gesture == "belly":
        hold = (cx, shoulder + 168 * s)
        limb(base, left, (cx - 22 * s, shoulder + 160 * s), 12 * s, skin + (255,))
        limb(base, right, (cx + 28 * s, shoulder + 156 * s), 12 * s, skin + (255,))
        hand(base, cx - 18 * s, shoulder + 164 * s, s, skin)
        hand(base, cx + 24 * s, shoulder + 160 * s, s, skin)
    elif gesture == "phone":
        hold = (cx + 8 * s, shoulder + 86 * s)
        limb(base, left, (cx - 16 * s, shoulder + 92 * s), 11 * s, skin + (255,))
        limb(base, right, (cx + 28 * s, shoulder + 88 * s), 11 * s, skin + (255,))
        hand(base, cx - 8 * s, shoulder + 96 * s, s, skin)
        hand(base, cx + 24 * s, shoulder + 92 * s, s, skin)
    elif gesture == "bag":
        hold = (cx + near * 78 * s, hip + 70 * s)
        limb(base, right if near > 0 else left, hold, 12 * s, skin + (255,))
        hand(base, hold[0], hold[1], s, skin)
    elif gesture == "open":
        for origin, end in ((left, (cx - 130 * s, shoulder + 70 * s)), (right, (cx + 132 * s, shoulder + 64 * s))):
            limb(base, origin, end, 11 * s, skin + (255,))
            hand(base, end[0], end[1], s * 1.15, skin)
        hold = (cx + 132 * s, shoulder + 64 * s)
    elif gesture == "cross":
        limb(base, left, (cx + 48 * s, shoulder + 70 * s), 12 * s, skin + (255,))
        limb(base, right, (cx - 48 * s, shoulder + 88 * s), 12 * s, skin + (255,))
        hold = (cx, shoulder + 78 * s)
    elif gesture == "run":
        hold = (cx + near * 150 * s, shoulder - 10 * s)
        limb(base, right if near > 0 else left, (cx + near * 90 * s, shoulder + 40 * s), 12 * s, skin + (255,))
        limb(base, (cx + near * 90 * s, shoulder + 40 * s), hold, 11 * s, skin + (255,))
        back = (cx - near * 120 * s, shoulder + 80 * s)
        limb(base, left if near > 0 else right, back, 11 * s, skin + (255,))
        hand(base, hold[0], hold[1], s, skin)
    elif gesture == "pocket":
        hold = (cx + near * 36 * s, hip + 10 * s)
        limb(base, right if near > 0 else left, hold, 12 * s, skin + (255,))
        hand(base, hold[0], hold[1], s, skin)
        other = left if near > 0 else right
        limb(base, other, (other[0], hip + 40 * s), 11 * s, skin + (255,))
    else:
        limb(base, left, (cx - 98 * s, hip + 46 * s), 11 * s, skin + (255,))
        limb(base, right, (cx + 102 * s, hip + 40 * s), 11 * s, skin + (255,))
        hand(base, cx - 98 * s, hip + 54 * s, s, skin)
        hand(base, cx + 102 * s, hip + 48 * s, s, skin)
        hold = (cx + 102 * s, hip + 48 * s)
    return hold


def prop_at(base: Image.Image, kind: str, x: float, y: float, s: float) -> None:
    draw = ImageDraw.Draw(base)
    if kind in {"phone", "phone_off"}:
        draw.rounded_rectangle([x - 28 * s, y - 48 * s, x + 28 * s, y + 48 * s], 6, fill=(24, 18, 16), outline=GOLD, width=3)
        draw.rectangle([x - 20 * s, y - 34 * s, x + 20 * s, y + 24 * s], fill=(236, 214, 180))
        if kind == "phone_off":
            draw.line([(x - 16 * s, y - 8 * s), (x + 16 * s, y + 16 * s)], fill=(168, 52, 46), width=3)
    elif kind == "bag":
        draw.rounded_rectangle([x - 36 * s, y - 10 * s, x + 36 * s, y + 70 * s], 6, fill=(62, 42, 30), outline=GOLD, width=3)
        draw.arc([x - 22 * s, y - 36 * s, x + 22 * s, y + 8 * s], 200, 340, fill=GOLD, width=4)
    elif kind == "flower":
        for i in range(6):
            a = math.tau * i / 6
            draw.ellipse([x + math.cos(a) * 16 * s - 9 * s, y + math.sin(a) * 16 * s - 9 * s, x + math.cos(a) * 16 * s + 9 * s, y + math.sin(a) * 16 * s + 9 * s], fill=(176, 64, 58))
        draw.ellipse([x - 7 * s, y - 7 * s, x + 7 * s, y + 7 * s], fill=GOLD)
        draw.line([(x, y + 8 * s), (x, y + 70 * s)], fill=(46, 90, 52), width=3)
    elif kind == "cup":
        draw.rounded_rectangle([x - 18 * s, y - 8 * s, x + 18 * s, y + 28 * s], 4, fill=(92, 58, 40))
        draw.ellipse([x - 20 * s, y - 16 * s, x + 20 * s, y + 6 * s], fill=(232, 196, 140))
        draw.arc([x + 14 * s, y - 4 * s, x + 34 * s, y + 22 * s], 280, 80, fill=CREAM, width=3)


def paint_person(
    base: Image.Image,
    cx: float,
    foot: float,
    scale: float,
    facing: str,
    build: str,
    pose: str,
    skin_i: int,
    hair: str,
    cloth_i: int,
    expr: str,
    gesture: str,
    seed: int,
) -> None:
    s = scale
    skin = SKIN[skin_i % len(SKIN)]
    hair_c = HAIR[seed % len(HAIR)]
    cloth, _fold, bands = CLOTH[cloth_i % len(CLOTH)]
    sign = 0 if facing == "front" else (1 if facing == "right" else -1)
    near = sign if sign else 1
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([cx - 110 * s, foot - 18 * s, cx + 120 * s, foot + 26 * s], fill=(40, 24, 16, 70))
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(5)))

    if pose == "curl":
        solid(base, [
            (cx - 170 * s, foot - 20 * s), (cx - 70 * s, foot - 250 * s), (cx + 40 * s, foot - 280 * s),
            (cx + 180 * s, foot - 90 * s), (cx + 140 * s, foot), (cx - 150 * s, foot + 6 * s),
        ], cloth)
        hy = foot - 230 * s
        hair_back(base, cx - 10 * s, hy, s * 0.8, hair, hair_c, seed)
        front_head(base, cx - 10 * s, hy, s * 0.82, skin, "man")
        draw = ImageDraw.Draw(base)
        features(draw, cx - 10 * s, hy, s * 0.82, expr, 0)
        hair_front(base, cx - 10 * s, hy, s * 0.8, hair, hair_c, seed, "front")
        return

    if pose == "sit":
        shoulder = foot - 310 * s
        hip = foot - 150 * s
    else:
        shoulder = foot - 450 * s
        hip = foot - 210 * s
    hy = shoulder - 150 * s
    scx = cx + (near * 36 * s if pose == "run" else 0)

    if build == "woman" and pose != "run":
        solid(base, [
            (scx - 78 * s, shoulder + 8 * s), (scx + 84 * s, shoulder),
            (scx + 168 * s, foot - 6 * s), (scx + 40 * s, foot + 4 * s),
            (scx - 150 * s, foot), (scx - 120 * s, hip),
        ], cloth)
        hem(ImageDraw.Draw(base), scx - 130 * s, scx + 145 * s, foot - 28 * s, bands)
        if gesture == "belly":
            paste_poly(base, blob(scx + 6 * s, shoulder + 188 * s, 92 * s, 84 * s, seed, 28), (232, 214, 198, 255))
            ImageDraw.Draw(base).arc([scx - 78 * s, shoulder + 150 * s, scx + 96 * s, shoulder + 300 * s], 200, 340, fill=INK, width=3)
        shoe(base, scx - 70 * s, foot, s, -1)
        shoe(base, scx + 70 * s, foot, s, 1)
    elif pose == "sit":
        solid(base, [
            (scx - 78 * s, shoulder), (scx + 82 * s, shoulder - 6 * s),
            (scx + 70 * s, hip), (scx - 66 * s, hip + 8 * s),
        ], cloth)
        solid(base, [
            (scx - 70 * s, hip), (scx + 50 * s, hip - 8 * s),
            (scx + 210 * s, hip + 36 * s), (scx + 180 * s, hip + 78 * s), (scx - 40 * s, hip + 48 * s),
        ], (36, 28, 24))
        solid(base, [
            (scx + 168 * s, hip + 48 * s), (scx + 210 * s, hip + 40 * s),
            (scx + 196 * s, foot), (scx + 150 * s, foot - 4 * s),
        ], (36, 28, 24))
        shoe(base, scx + 188 * s, foot, s, 1)
    elif pose == "run":
        solid(base, [
            (scx - 70 * s, shoulder), (scx + 78 * s, shoulder - 16 * s),
            (scx + 58 * s, hip), (scx - 62 * s, hip + 10 * s),
        ], cloth)
        solid(base, [
            (scx - 20 * s, hip), (scx + 40 * s, hip - 8 * s),
            (scx + near * 150 * s, foot - 20 * s), (scx + near * 108 * s, foot),
        ], (36, 28, 24))
        solid(base, [
            (scx - 40 * s, hip + 6 * s), (scx + 10 * s, hip),
            (scx - near * 130 * s, foot - 30 * s), (scx - near * 80 * s, foot - 8 * s),
        ], (48, 36, 30))
        shoe(base, scx + near * 130 * s, foot - 8 * s, s, near)
        shoe(base, scx - near * 110 * s, foot - 16 * s, s, -near)
    else:
        solid(base, [
            (scx - 86 * s, shoulder + 6 * s), (scx + 90 * s, shoulder - 4 * s),
            (scx + 72 * s, hip), (scx - 68 * s, hip + 8 * s),
        ], cloth)
        solid(base, [
            (scx - 66 * s, hip), (scx - 6 * s, hip + 4 * s),
            (scx - 2 * s, foot - 8 * s), (scx - 78 * s, foot),
        ], (36, 28, 24))
        solid(base, [
            (scx + 8 * s, hip + 2 * s), (scx + 68 * s, hip),
            (scx + 84 * s, foot), (scx + 8 * s, foot - 6 * s),
        ], (28, 22, 18))
        shoe(base, scx - 40 * s, foot, s, -1)
        shoe(base, scx + 46 * s, foot, s, 1)
        if build == "elder":
            paste_poly(base, [
                (scx - 100 * s, shoulder - 10 * s), (scx + 20 * s, shoulder - 30 * s),
                (scx + 46 * s, hip + 20 * s), (scx - 30 * s, foot - 20 * s), (scx - 110 * s, hip),
            ], (236, 226, 210, 230))
            ImageDraw.Draw(base).line([(scx - 96 * s, shoulder), (scx - 24 * s, foot - 30 * s)], fill=(168, 52, 46, 220), width=5)

    paste_poly(base, [
        (scx - 20 * s, hy + 78 * s), (scx + 20 * s, hy + 74 * s),
        (scx + 28 * s, shoulder + 16 * s), (scx - 26 * s, shoulder + 18 * s),
    ], skin + (255,))
    hair_back(base, scx, hy, s, hair, hair_c, seed)
    front_head(base, scx, hy, s, skin, build)
    draw = ImageDraw.Draw(base)
    ear = tuple(max(0, c - 18) for c in skin)
    draw.ellipse([scx - 84 * s, hy + 4 * s, scx - 60 * s, hy + 36 * s], fill=ear + (255,))
    draw.ellipse([scx + 60 * s, hy + 4 * s, scx + 84 * s, hy + 36 * s], fill=ear + (255,))
    features(draw, scx, hy, s, expr, float(sign))
    if build == "elder" or hair == "beard":
        beard(base, scx, hy, s)
    if hair == "mustache":
        draw.arc([scx - 22 * s, hy + 40 * s, scx + 22 * s, hy + 62 * s], 10, 170, fill=(42, 28, 20), width=4)
    if expr == "shy":
        for dx in (-18, 2, 20):
            draw.ellipse([scx + dx * s, hy - 20 * s, scx + dx * s + 7 * s, hy - 6 * s], fill=(120, 170, 190, 180))
    if build == "woman" and cloth_i % 2 == 0:
        draw.ellipse([scx - 78 * s, hy + 22 * s, scx - 66 * s, hy + 34 * s], outline=GOLD, width=2)
    hair_front(base, scx, hy, s, hair, hair_c, seed, facing)
    arm_gesture = "run" if pose == "run" else ("reach" if gesture == "flower" else ("phone" if gesture == "phone_off" else gesture))
    hold = arms(base, scx, shoulder, hip, hy, s, skin, arm_gesture, near)
    if gesture in {"phone", "phone_off"}:
        prop_at(base, "phone_off" if gesture == "phone_off" else "phone", hold[0], hold[1], s)
    elif gesture == "bag":
        prop_at(base, "bag", hold[0], hold[1] + 10 * s, s)
    elif gesture == "flower":
        prop_at(base, "flower", hold[0] + near * 10 * s, hold[1] - 36 * s, s)
    elif gesture == "cup":
        prop_at(base, "cup", scx + near * 70 * s, shoulder + 40 * s, s)


def body_guard(mask: Image.Image, people: list) -> Image.Image:
    draw = ImageDraw.Draw(mask)
    for person in people:
        cx, foot, scale = person[0], person[1], person[2]
        top = foot - 720 * scale
        draw.ellipse([cx - 200 * scale, top, cx + 210 * scale, foot + 30 * scale], fill=0)
    return mask


def child(base: Image.Image, cx: float, foot: float, s: float, skin, cloth) -> None:
    hy = foot - 120 * s
    paste_poly(base, blob(cx, hy, 36 * s, 40 * s, 3, 16), skin + (255,))
    solid(base, [(cx - 28 * s, hy + 30 * s), (cx + 30 * s, hy + 26 * s), (cx + 40 * s, foot), (cx - 36 * s, foot)], cloth)
    ImageDraw.Draw(base).arc([cx - 10 * s, hy + 6 * s, cx + 12 * s, hy + 22 * s], 10, 170, fill=ROSE, width=2)


def rain(base: Image.Image) -> None:
    draw = ImageDraw.Draw(base)
    rnd = random.Random(15)
    for _ in range(80):
        x, y = rnd.randint(40, W - 40), rnd.randint(40, H - 40)
        draw.line([(x, y), (x - 16, y + 42)], fill=(210, 220, 228, 140), width=2)


def story_front(base: Image.Image, key: str) -> None:
    draw = ImageDraw.Draw(base)
    if key == "01":
        draw.rectangle([190, 760, 214, 1040], fill=CREAM)
        draw.rectangle([400, 740, 424, 1020], fill=CREAM)
        draw.polygon([(170, 760), (450, 720), (450, 770), (170, 812)], fill=CREAM)
        draw.polygon([(170, 1000), (460, 960), (460, 1010), (170, 1050)], fill=CREAM)
        draw.rectangle([200, 1030, 224, 1280], fill=CREAM)
        draw.rectangle([400, 1000, 424, 1260], fill=CREAM)
        paste_poly(base, [(200, 980), (430, 950), (400, 1100), (190, 1120)], (244, 238, 228, 235))
        draw.line([(210, 1080), (390, 1050)], fill=(168, 52, 46), width=5)
    elif key == "02":
        draw.line([(430, 430), (760, 860)], fill=(168, 52, 46), width=10)
        draw.line([(740, 450), (450, 840)], fill=(168, 52, 46), width=10)
        draw.ellipse([250, 1288, 330, 1368], fill=(168, 52, 46))
        draw.ellipse([300, 1288, 380, 1368], fill=(168, 52, 46))
        draw.polygon([(250, 1320), (380, 1320), (315, 1420)], fill=(168, 52, 46))
        draw.polygon([(300, 1360), (430, 1340), (460, 1390), (320, 1410)], fill=(62, 42, 32))
    elif key == "03":
        draw.line([(400, 760), (600, 700), (800, 760)], fill=GOLD, width=6)
        draw.ellipse([578, 678, 622, 722], outline=CREAM, width=4)
        draw.ellipse([590, 692, 604, 708], fill=INK)
    elif key == "05":
        draw.ellipse([545, 860, 655, 940], outline=GOLD, width=10)
        draw.ellipse([575, 888, 625, 918], outline=CREAM, width=4)
        draw.polygon([(600, 1020), (760, 1280), (440, 1280)], outline=CREAM, width=6)
        draw.rectangle([560, 1120, 640, 1280], outline=GOLD, width=4)
        child(base, 540, 1540, 1.05, SKIN[2], CLOTH[3][0])
        child(base, 680, 1560, 0.85, SKIN[4], CLOTH[0][0])
        draw.ellipse([575, 1088, 625, 1138], fill=SKIN[0])
    elif key == "06":
        draw.ellipse([470, 280, 560, 360], outline=CREAM, width=8)
        draw.ellipse([640, 280, 730, 360], outline=CREAM, width=8)
        draw.ellipse([500, 308, 524, 332], fill=INK)
        draw.ellipse([670, 308, 694, 332], fill=INK)
    elif key == "07":
        draw.ellipse([160, 220, 340, 400], fill=(232, 186, 96))
        draw.ellipse([860, 240, 1040, 420], outline=CREAM, width=8)
        paste_poly(base, blob(980, 520, 70, 80, 7, 18), SKIN[3] + (255,))
        draw.arc([930, 540, 1030, 600], 10, 170, fill=ROSE, width=3)
    elif key == "08":
        draw.ellipse([860, 180, 1040, 360], outline=CREAM, width=6)
    elif key == "10":
        draw.rounded_rectangle([140, 260, 420, 400], 28, outline=CREAM, width=5)
        draw.rounded_rectangle([760, 240, 1060, 390], 28, outline=GOLD, width=5)
        draw.text((210, 300), "Hi", fill=CREAM)
        draw.text((860, 285), "Hi", fill=GOLD)
        for i, x in enumerate((180, 230, 280)):
            draw.ellipse([x, 1280 + (i % 2) * 20, x + 36, 1310 + (i % 2) * 20], outline=CREAM, width=3)
    elif key == "11":
        paste_poly(base, [(700, 620), (860, 560), (900, 640), (760, 720)], SKIN[4] + (255,))
        for i in range(4):
            draw.rounded_rectangle([820 + i * 8, 520, 836 + i * 8, 600], 4, fill=SKIN[4])
    elif key == "14":
        palm = SKIN[2]
        draw.ellipse([760, 700, 980, 960], fill=palm)
        for i in range(4):
            draw.rounded_rectangle([790 + i * 46, 520, 828 + i * 46, 730], 12, fill=palm)
        draw.rounded_rectangle([930, 760, 1020, 900], 14, fill=palm)
        for i in range(6):
            a = math.tau * i / 6
            draw.ellipse([300 + math.cos(a) * 28 - 16, 1240 + math.sin(a) * 28 - 16, 300 + math.cos(a) * 28 + 16, 1240 + math.sin(a) * 28 + 16], fill=(176, 64, 58))
    elif key == "15":
        paste_poly(base, [(860, 980), (1120, 940), (1160, 1320), (820, 1340)], (236, 226, 210, 200))
        draw.line([(880, 1280), (1100, 1240)], fill=(168, 52, 46), width=6)
    elif key == "16":
        for i in range(5):
            draw.line([(180, 1180 + i * 24), (420, 1140 + i * 24)], fill=CREAM, width=5)
    elif key == "19":
        for i in range(8):
            a = math.tau * i / 8
            x, y = 620 + math.cos(a) * 250, 460 + math.sin(a) * 140
            draw.ellipse([x - 22, y - 22, x + 22, y + 22], outline=GOLD, width=3)
        draw.arc([120, 860, 520, 1320], 200, 20, fill=CREAM, width=16)
        child(base, 300, 1240, 1.3, SKIN[2], CLOTH[0][0])
    elif key == "20":
        draw.polygon([(430, 1180), (760, 1140), (760, 1220), (430, 1240)], fill=(92, 58, 40))
        draw.polygon(
            [(820, 520), (940, 430), (1020, 470), (980, 540), (1120, 500), (1040, 640), (860, 660)],
            fill=(232, 214, 180),
        )
        draw.line([(940, 450), (980, 390)], fill=GOLD, width=5)
        draw.line([(700, 430), (860, 520)], fill=CREAM, width=4)
    elif key == "21":
        paste_poly(base, blob(900, 1140, 78, 96, 21, 22), CREAM + (255,))
        draw.ellipse([860, 1110, 900, 1150], fill=INK)
        draw.ellipse([930, 1110, 970, 1150], fill=INK)
        draw.arc([870, 1170, 960, 1220], 15, 165, fill=INK, width=3)
    elif key == "22":
        draw.rounded_rectangle([720, 460, 1080, 1120], 12, fill=(62, 40, 30), outline=GOLD, width=6)
        draw.rectangle([770, 530, 1030, 900], outline=CREAM, width=4)
        draw.ellipse([980, 760, 1020, 800], fill=GOLD)
    elif key == "23":
        draw.rounded_rectangle([700, 380, 1100, 1180], 20, outline=GOLD, width=8)
        paste_poly(base, blob(900, 700, 80, 100, 23, 20), (90, 58, 46, 255))
        draw.line([(860, 820), (940, 820)], fill=GOLD, width=4)
        draw.ellipse([860, 660, 890, 690], fill=INK)
        draw.ellipse([920, 660, 950, 690], fill=INK)
    elif key == "24":
        draw.rounded_rectangle([140, 180, 1060, 560], 30, fill=(36, 110, 72), outline=CREAM, width=5)
        for i in range(5):
            draw.rounded_rectangle([180 + i * 160, 230, 310 + i * 160, 380], 8, fill=(236, 226, 204))
        draw.rectangle([500, 400, 680, 540], fill=(24, 70, 48))
        draw.ellipse([240, 500, 360, 620], fill=(28, 22, 18))
        draw.ellipse([840, 500, 960, 620], fill=(28, 22, 18))
        for i, dx in enumerate((-16, 0, 18)):
            draw.ellipse([700 + dx, 1080 + i * 8, 728 + dx, 1106 + i * 8], fill=GOLD, outline=INK)
    elif key == "25":
        draw.line([(780, 1360), (780, 980)], fill=CREAM, width=18)
        draw.line([(780, 980), (520, 560)], fill=GOLD, width=18)
        draw.line([(780, 980), (1080, 540)], fill=CREAM, width=18)
    elif key == "26":
        draw.ellipse([480, 180, 740, 440], fill=(232, 186, 96))
        draw.polygon([(360, 1120), (860, 1080), (860, 1160), (360, 1180)], fill=(92, 58, 40))
    elif key == "27":
        draw.line([(560, 980), (700, 980)], fill=(168, 52, 46), width=6)
    elif key == "28":
        draw.rounded_rectangle([500, 1180, 700, 1320], 8, outline=CREAM, width=4)
        draw.line([(520, 1200), (680, 1300)], fill=(168, 52, 46), width=5)
        draw.line([(680, 1200), (520, 1300)], fill=(168, 52, 46), width=5)


# cx, foot, scale, facing, build, pose, skin, hair, cloth, expr, gesture
People = list[tuple]
SCENES: dict[str, dict] = {
    "end": {"people": [(760, 1480, 0.74, "left", "woman", "stand", 3, "bun", 2, "closed", "side")]},
    "01": {"people": [(860, 1540, 1.05, "front", "man", "sit", 0, "beard", 3, "down", "think")]},
    "02": {"people": [(900, 1520, 1.02, "left", "man", "stand", 2, "afro", 1, "worry", "reach")]},
    "03": {"people": [
        (300, 1500, 0.98, "right", "man", "stand", 1, "fade", 2, "shy", "side"),
        (900, 1500, 0.98, "left", "woman", "stand", 4, "long", 0, "flat", "cross"),
    ]},
    "05": {"people": [
        (380, 1500, 0.92, "right", "man", "stand", 0, "crop", 4, "smile", "reach"),
        (820, 1500, 0.92, "left", "woman", "stand", 3, "braids", 5, "smile", "reach"),
    ]},
    "06": {"people": [
        (880, 1460, 0.95, "left", "man", "stand", 4, "bald", 2, "flat", "reach"),
        (520, 1520, 1.02, "front", "man", "stand", 1, "afro", 0, "worry", "side"),
    ]},
    "07": {"people": [(620, 1500, 1.0, "front", "man", "stand", 2, "braids", 3, "smile", "flower")]},
    "08": {"people": [(640, 1500, 1.02, "front", "man", "sit", 0, "fade", 1, "worry", "phone_off")]},
    "10": {"people": [(960, 1520, 1.05, "front", "woman", "stand", 3, "wrap", 0, "worry", "belly")]},
    "11": {"people": [
        (420, 1520, 1.0, "front", "man", "stand", 2, "crop", 2, "shy", "side"),
        (860, 1480, 0.96, "left", "woman", "stand", 4, "braids", 5, "soft", "reach"),
    ]},
    "14": {"people": [(520, 1500, 1.05, "front", "woman", "stand", 3, "long", 0, "worry", "side")]},
    "15": {"people": [(480, 1500, 1.15, "front", "man", "curl", 1, "wrap", 2, "closed", "side")], "rain": True},
    "16": {"people": [
        (980, 1500, 0.88, "left", "woman", "stand", 4, "wrap", 0, "flat", "side"),
        (520, 1500, 1.05, "right", "man", "run", 2, "crop", 3, "open", "side"),
    ]},
    "18": {"people": [(620, 1520, 1.08, "front", "man", "sit", 0, "afro", 5, "down", "phone")]},
    "19": {"people": [(760, 1500, 1.0, "front", "man", "sit", 1, "beard", 1, "worry", "think")]},
    "20": {"people": [(460, 1460, 0.95, "front", "elder", "sit", 4, "bald", 3, "closed", "cup")]},
    "21": {"people": [(560, 1520, 1.05, "right", "man", "stand", 2, "fade", 0, "smile", "reach")]},
    "22": {"people": [(420, 1520, 1.05, "right", "man", "stand", 0, "crop", 4, "flat", "bag")]},
    "23": {"people": [(420, 1500, 1.02, "right", "man", "stand", 1, "mustache", 5, "flat", "side")]},
    "24": {"people": [
        (250, 1420, 0.72, "right", "man", "stand", 2, "crop", 4, "open", "pocket"),
        (760, 1320, 0.62, "left", "man", "stand", 0, "fade", 1, "smile", "open"),
    ]},
    "25": {"people": [(340, 1520, 1.02, "right", "man", "stand", 3, "afro", 2, "worry", "think")]},
    "26": {"people": [
        (340, 1500, 0.9, "right", "man", "stand", 1, "afro", 1, "smile", "cup"),
        (860, 1500, 0.9, "left", "woman", "stand", 4, "bun", 3, "open", "cup"),
    ]},
    "27": {"people": [
        (340, 1500, 0.95, "right", "man", "stand", 0, "beard", 4, "worry", "reach"),
        (860, 1500, 0.98, "front", "woman", "stand", 3, "long", 5, "down", "phone"),
    ]},
    "28": {"people": [
        (340, 1500, 0.95, "right", "man", "stand", 2, "crop", 2, "soft", "open"),
        (860, 1500, 0.95, "left", "woman", "stand", 4, "braids", 0, "soft", "open"),
    ]},
}

KEEP = {"cover", "end", "04", "09", "12", "13", "17"}


def compose(key: str, spec: dict) -> None:
    plate = Image.open(OLD / f"{key}.jpg").convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    base = plate.convert("RGBA")
    for index, person in enumerate(spec["people"]):
        cx, foot, scale, facing, build, pose, skin_i, hair, cloth_i, expr, gesture = person
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        paint_person(
            layer, cx, foot, scale, facing, build, pose, skin_i, hair, cloth_i, expr, gesture,
            seed=index * 17 + sum(ord(c) for c in key) + 3,
        )
        base.alpha_composite(layer)
    base = Image.composite(plate.convert("RGBA"), base, body_guard(motif_mask(plate), spec["people"]))
    story_front(base, key)
    if spec.get("rain"):
        rain(base)
    grain = Image.effect_noise((W, H), 12).convert("L")
    base = Image.alpha_composite(base, Image.merge("RGBA", (grain, grain, grain, Image.new("L", (W, H), 14))))
    rgb = base.convert("RGB")
    rgb.save(OUT / f"{key}.jpg", quality=86, optimize=True)
    print(key, (OUT / f"{key}.jpg").stat().st_size)


def main() -> None:
    for key, spec in SCENES.items():
        if key in KEEP:
            print("keep", key)
            continue
        compose(key, spec)


if __name__ == "__main__":
    main()
