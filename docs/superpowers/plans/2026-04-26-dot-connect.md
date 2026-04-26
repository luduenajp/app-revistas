# Dot-Connect Activity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a "unir con puntos" (connect-the-dots) activity generator that traces a PNG silhouette, samples N equidistant points, and outputs a PDF page with numbered dots.

**Architecture:** A new `generate_dot_connect()` function in `src/generators/dot_connect.py` loads a PNG from `src/shapes/`, traces its contour with `skimage.measure.find_contours`, samples N equidistant points, and renders an SVG. A new Jinja2 template and renderer function wrap it into a printable HTML page, following the exact same pattern as the existing maze and word-search activities.

**Tech Stack:** Python 3.11+, Pillow (image I/O + shape generation), scikit-image (contour detection), numpy (arc-length resampling), Jinja2 (templating), Playwright (PDF export — already installed).

---

## Task 1: Add dependencies and create PNG shape silhouettes

**Files:**
- Modify: `requirements.txt`
- Create: `src/shapes/generate_shapes.py`
- Create: `src/shapes/estrella.png`, `src/shapes/cohete.png`, `src/shapes/corazon.png`, `src/shapes/dinosaurio.png`

- [ ] **Step 1: Add Pillow and scikit-image to requirements.txt**

Replace the contents of `requirements.txt` with:

```
mazelib==0.9.16
playwright==1.44.0
jinja2==3.1.4
pytest==8.2.2
pytest-asyncio==0.23.7
numpy==1.26.4
Pillow>=10.0.0
scikit-image>=0.22.0
```

- [ ] **Step 2: Install the new dependencies**

```bash
source .venv/bin/activate
pip install Pillow scikit-image
```

Expected: both packages install without errors.

- [ ] **Step 3: Create src/shapes/ and the shape generator script**

Create `src/shapes/generate_shapes.py`:

```python
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
```

- [ ] **Step 4: Run the generator script**

```bash
source .venv/bin/activate
python src/shapes/generate_shapes.py
```

Expected output:
```
Generating shapes...
  created estrella.png
  created corazon.png
  created cohete.png
  created dinosaurio.png
Done. 4 shapes created in src/shapes/
```

- [ ] **Step 5: Verify the PNGs look correct**

```bash
python - <<'EOF'
from PIL import Image
import os
for name in ["estrella", "corazon", "cohete", "dinosaurio"]:
    img = Image.open(f"src/shapes/{name}.png")
    print(f"{name}: {img.size} mode={img.mode}")
EOF
```

Expected: each shows `(300, 300) mode=L`.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt src/shapes/
git commit -m "feat: add Pillow+scikit-image deps and initial shape PNGs"
```

---

## Task 2: Write failing tests for generate_dot_connect

**Files:**
- Create: `tests/test_dot_connect.py`

- [ ] **Step 1: Create the test file**

Create `tests/test_dot_connect.py`:

```python
import pytest
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw

from src.generators.dot_connect import generate_dot_connect, DotConnectResult


@pytest.fixture
def circle_shape(tmp_path, monkeypatch):
    """A clean circle PNG used as a test shape (self-contained, no src/shapes dependency)."""
    img = Image.new("L", (200, 200), 255)
    draw = ImageDraw.Draw(img)
    draw.ellipse([20, 20, 180, 180], fill=0)
    shapes_dir = tmp_path / "shapes"
    shapes_dir.mkdir()
    img.save(shapes_dir / "circle.png")

    import src.generators.dot_connect as mod
    monkeypatch.setattr(mod, "_SHAPES_DIR", shapes_dir)
    return "circle"


def test_returns_dot_connect_result(circle_shape):
    result = generate_dot_connect(circle_shape, "easy")
    assert isinstance(result, DotConnectResult)


def test_easy_returns_15_dots(circle_shape):
    result = generate_dot_connect(circle_shape, "easy")
    assert len(result.dots) == 15


def test_hard_returns_28_dots(circle_shape):
    result = generate_dot_connect(circle_shape, "hard")
    assert len(result.dots) == 28


def test_dots_within_bounding_box(circle_shape):
    w, h = 320, 320
    result = generate_dot_connect(circle_shape, "easy", width_px=w, height_px=h)
    for x, y in result.dots:
        assert 0 <= x <= w, f"x={x} out of bounds"
        assert 0 <= y <= h, f"y={y} out of bounds"


def test_result_fields(circle_shape):
    result = generate_dot_connect(circle_shape, "hard")
    assert result.label == circle_shape
    assert result.difficulty == "hard"


def test_svg_contains_circles_and_numbers(circle_shape):
    result = generate_dot_connect(circle_shape, "easy")
    assert "<svg" in result.svg_html
    assert "</svg>" in result.svg_html
    # 15 dots → 15 <circle> elements and numbers 1..15
    assert result.svg_html.count("<circle") == 15
    assert ">1<" in result.svg_html
    assert ">15<" in result.svg_html


def test_invalid_difficulty_raises(circle_shape):
    with pytest.raises(ValueError, match="difficulty"):
        generate_dot_connect(circle_shape, "medium")


def test_missing_figure_raises(tmp_path, monkeypatch):
    import src.generators.dot_connect as mod
    monkeypatch.setattr(mod, "_SHAPES_DIR", tmp_path)
    with pytest.raises(FileNotFoundError, match="nonexistent"):
        generate_dot_connect("nonexistent", "easy")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
source .venv/bin/activate
pytest tests/test_dot_connect.py -v 2>&1 | head -30
```

Expected: `ImportError: cannot import name 'generate_dot_connect'` or similar — the module doesn't exist yet.

- [ ] **Step 3: Commit the failing tests**

```bash
git add tests/test_dot_connect.py
git commit -m "test: add failing tests for dot_connect generator"
```

---

## Task 3: Implement the dot_connect generator

**Files:**
- Create: `src/generators/dot_connect.py`

- [ ] **Step 1: Create the generator module**

Create `src/generators/dot_connect.py`:

```python
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
```

- [ ] **Step 2: Run tests and verify they pass**

```bash
source .venv/bin/activate
pytest tests/test_dot_connect.py -v
```

Expected: all 8 tests pass.

- [ ] **Step 3: Commit**

```bash
git add src/generators/dot_connect.py
git commit -m "feat: implement dot_connect generator with PNG contour tracing"
```

---

## Task 4: Add the Jinja2 template and renderer function

**Files:**
- Create: `src/templates/dot_connect_activity.html.j2`
- Modify: `src/renderers/html_page.py`

- [ ] **Step 1: Create the template**

Create `src/templates/dot_connect_activity.html.j2`:

```jinja
{% extends "base.html.j2" %}
{% block content %}
<h1>{{ title }}</h1>
{% if subtitle %}<p>{{ subtitle }}</p>{% endif %}
<div class="dot-connect-container">
  {{ dot_svg | safe }}
</div>
{% endblock %}
```

- [ ] **Step 2: Add the dot-connect CSS to base.html.j2**

In `src/templates/base.html.j2`, add this rule after the existing `.maze-container svg` rule (around line 92):

```css
  /* ── Unir con puntos ──────────────────────────────────────── */
  .dot-connect-container svg { max-width: 100%; height: auto; }
```

- [ ] **Step 3: Add render_dot_connect_page to html_page.py**

In `src/renderers/html_page.py`, add after `render_word_search_page`:

```python
def render_dot_connect_page(
    dot_svg: str,
    title: str = "¡Uní los puntos!",
    subtitle: str = "",
    style: dict | None = None,
) -> str:
    ctx = {**(style or {}), "title": title, "subtitle": subtitle, "dot_svg": dot_svg}
    return _env.get_template("dot_connect_activity.html.j2").render(**ctx)
```

- [ ] **Step 4: Verify the renderer works with a quick smoke test**

```bash
source .venv/bin/activate
python - <<'EOF'
from src.generators.dot_connect import generate_dot_connect
from src.renderers.html_page import render_dot_connect_page

dc = generate_dot_connect("estrella", "easy")
html = render_dot_connect_page(dc.svg_html, title="Test", subtitle="15 puntos")
assert "<svg" in html
assert "¡Uní los puntos!" not in html  # custom title overrides default
assert "Test" in html
assert html.count("<circle") == 15
print("OK — renderer smoke test passed")
EOF
```

Expected: `OK — renderer smoke test passed`

- [ ] **Step 5: Run all existing tests to confirm no regressions**

```bash
source .venv/bin/activate
pytest -v
```

Expected: all tests pass (maze + word_search + dot_connect).

- [ ] **Step 6: Commit**

```bash
git add src/templates/dot_connect_activity.html.j2 src/templates/base.html.j2 src/renderers/html_page.py
git commit -m "feat: add dot_connect template and render_dot_connect_page"
```

---

## Task 5: Integrate into demo and generate the PDF

**Files:**
- Modify: `demo/demo_dinos.py`

- [ ] **Step 1: Add dot-connect generation to the demo**

In `demo/demo_dinos.py`, add the import at the top with the others:

```python
from src.generators.dot_connect import generate_dot_connect
from src.renderers.html_page import render_maze_page, render_word_search_page, render_dot_connect_page
```

Then add this block at the end of `main()`, after the word-search block:

```python
    # Unir con puntos
    dc = generate_dot_connect("dinosaurio", difficulty="easy")
    dc_html = render_dot_connect_page(
        dc.svg_html,
        title="¡Uní los puntos y descubrí el dino!",
        subtitle=f"Empezá por el 1 y seguí en orden. ({len(dc.dots)} puntos)",
        style=STYLE_INFANTIL,
    )
    pdf3 = export_html_to_pdf(dc_html, OUT / "dinos_puntos.pdf")
    print(f"✓ Unir con puntos: {pdf3}")
```

- [ ] **Step 2: Run the demo end-to-end**

```bash
source .venv/bin/activate
python demo/demo_dinos.py
```

Expected output:
```
✓ Laberinto: .../output/dinos_laberinto.pdf
✓ Sopa de letras: .../output/dinos_sopa.pdf
✓ Unir con puntos: .../output/dinos_puntos.pdf
```

- [ ] **Step 3: Open the generated PDF and verify**

```bash
open output/dinos_puntos.pdf
```

Verify: A4 page with title "¡Uní los puntos y descubrí el dino!", subtitle "Empezá por el 1 y seguí en orden. (15 puntos)", and 15 numbered red dots.

- [ ] **Step 4: Run the full test suite one final time**

```bash
source .venv/bin/activate
pytest -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add demo/demo_dinos.py
git commit -m "feat: integrate dot-connect into dinos demo, generates dinos_puntos.pdf"
```
