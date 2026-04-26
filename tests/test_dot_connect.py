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
