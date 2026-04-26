"""Generates the initial PNG silhouettes for the dot-connect activity.
Run: python src/shapes/generate_shapes.py
Outputs black-on-white 300x300 px PNGs in this directory.
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).parent
SIZE = 300
CX, CY = SIZE // 2, SIZE // 2


def _save(pts: list[tuple[float, float]], name: str) -> None:
    img = Image.new("L", (SIZE, SIZE), 255)
    draw = ImageDraw.Draw(img)
    draw.polygon(pts, fill=0)
    img.save(OUT / name)
    print(f"  created {name}")


def _star(cx: float, cy: float, r_outer: float, r_inner: float, n: int = 5):
    pts = []
    for i in range(n * 2):
        angle = math.pi * i / n - math.pi / 2
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts


def _heart(cx: float, cy: float, scale: float = 8.5):
    pts = []
    for deg in range(0, 360, 4):
        t = math.radians(deg)
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * scale, cy + y * scale + 15))
    return pts


if __name__ == "__main__":
    print("Generating shapes...")

    # Estrella (5-pointed star)
    _save(_star(CX, CY, r_outer=125, r_inner=52), "estrella.png")

    # Corazón
    _save(_heart(CX, CY), "corazon.png")

    # Cohete (nose tip → right shoulder → right fin → base → left fin → left shoulder)
    cohete = [
        (CX,       20),   # nose tip
        (CX + 42,  85),   # right shoulder
        (CX + 42, 205),   # right body lower
        (CX + 72, 268),   # right fin tip
        (CX + 42, 245),   # right fin inner
        (CX + 42, 285),   # right base
        (CX - 42, 285),   # left base
        (CX - 42, 245),   # left fin inner
        (CX - 72, 268),   # left fin tip
        (CX - 42, 205),   # left body lower
        (CX - 42,  85),   # left shoulder
    ]
    _save(cohete, "cohete.png")

    # Dinosaurio (brachiosaurus, facing left, clockwise from snout)
    dino = [
        (30,  90),   # snout tip
        (55,  65),   # head top
        (80,  48),   # lower neck
        (110, 30),   # neck arch top
        (140, 48),   # neck right
        (170, 68),   # shoulder
        (205, 65),   # back mid
        (250, 90),   # back right
        (278, 118),  # tail tip
        (260, 148),  # tail base bottom
        (208, 148),  # rump
        (222, 265),  # back leg right
        (200, 270),  # between back legs
        (180, 270),  # between front/back legs
        (158, 268),  # front leg right
        (140, 265),  # front leg left
        (118, 148),  # chest
        (90,  165),  # neck front lower
        (52,  128),  # chin/throat
    ]
    _save(dino, "dinosaurio.png")

    print("Done. 4 shapes created in src/shapes/")
