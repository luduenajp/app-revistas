import pytest
from pathlib import Path
from src.renderers.pdf_export import export_html_to_pdf


def test_pdf_is_created(tmp_path):
    html = "<html><body><h1>Test</h1></body></html>"
    out = tmp_path / "test.pdf"
    result = export_html_to_pdf(html, out)
    assert result.exists()
    assert result.stat().st_size > 1000  # Al menos 1KB


def test_returns_path(tmp_path):
    out = tmp_path / "out.pdf"
    result = export_html_to_pdf("<html><body>Hi</body></html>", out)
    assert isinstance(result, Path)
    assert result == out


def test_real_page_pdf(tmp_path):
    from src.generators.maze import generate_maze
    from src.renderers.html_page import render_maze_page
    maze = generate_maze(7, 7, seed=42)
    html = render_maze_page(maze.svg_html, title="Laberinto Test")
    out = tmp_path / "maze.pdf"
    result = export_html_to_pdf(html, out)
    assert result.exists()
    assert result.stat().st_size > 5000
