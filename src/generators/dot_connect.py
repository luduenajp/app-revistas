from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image
from skimage.measure import find_contours

_SHAPES_DIR = Path(__file__).parent.parent / "shapes"
_DIFFICULTY = {"easy": 15, "hard": 28}


@dataclass
class DotConnectResult:
    dots: list[tuple[float, float]]
    label: str
    difficulty: str
    svg_html: str


def generate_dot_connect(
    figure: str,
    difficulty: str = "easy",
    width_px: int = 400,
    height_px: int = 400,
) -> DotConnectResult:
    if difficulty not in _DIFFICULTY:
        raise ValueError(f"difficulty must be 'easy' or 'hard', got {difficulty!r}")

    path = _SHAPES_DIR / f"{figure}.png"
    if not path.exists():
        raise FileNotFoundError(f"Shape '{figure}' not found in {_SHAPES_DIR}")

    n_dots = _DIFFICULTY[difficulty]

    img = Image.open(path).convert("L")
    binary = (np.array(img) < 128).astype(float)

    contours = find_contours(binary, level=0.5)
    if not contours:
        raise ValueError(f"No contour found in shape '{figure}'")

    contour = max(contours, key=len)  # (N, 2) array of (row, col)

    sampled = _resample_contour(contour, n_dots)

    img_h, img_w = binary.shape
    dots = [
        (col / img_w * width_px, row / img_h * height_px)
        for row, col in sampled
    ]

    svg_html = _render_svg(dots, width_px, height_px)
    return DotConnectResult(dots=dots, label=figure, difficulty=difficulty, svg_html=svg_html)


def _resample_contour(contour: np.ndarray, n: int) -> list[tuple[float, float]]:
    diffs = np.diff(contour, axis=0)
    seg_lengths = np.hypot(diffs[:, 0], diffs[:, 1])
    cum_len = np.concatenate([[0.0], np.cumsum(seg_lengths)])
    total_len = cum_len[-1]

    targets = np.linspace(0, total_len, n, endpoint=False)
    rows = np.interp(targets, cum_len, contour[:, 0])
    cols = np.interp(targets, cum_len, contour[:, 1])
    return list(zip(rows.tolist(), cols.tolist()))


def _render_svg(dots: list[tuple[float, float]], width_px: int, height_px: int) -> str:
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_px} {height_px}" '
        f'width="{width_px}" height="{height_px}" style="display:block;max-width:100%;">',
        f'<rect width="{width_px}" height="{height_px}" fill="white"/>',
    ]

    for i, (x, y) in enumerate(dots):
        cx, cy = round(x, 1), round(y, 1)
        if x > width_px * 0.8:
            tx, anchor = round(cx - 9, 1), "end"
        else:
            tx, anchor = round(cx + 9, 1), "start"

        lines.append(
            f'<circle cx="{cx}" cy="{cy}" r="5" fill="var(--color-primary, #e74c3c)"/>'
        )
        lines.append(
            f'<text x="{tx}" y="{round(cy + 4, 1)}" font-size="11" '
            f'font-family="sans-serif" font-weight="700" '
            f'text-anchor="{anchor}" fill="var(--color-text, #2c3e50)">{i + 1}</text>'
        )

    lines.append("</svg>")
    return "\n".join(lines)
