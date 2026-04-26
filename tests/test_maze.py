import pytest
from src.generators.maze import generate_maze, MazeResult


def test_returns_maze_result():
    result = generate_maze(5, 5, seed=42)
    assert isinstance(result, MazeResult)


def test_grid_dimensions():
    result = generate_maze(5, 7, seed=42)
    # mazelib grid: (2*rows+1) x (2*cols+1)
    assert len(result.grid) == 11  # 2*5+1
    assert len(result.grid[0]) == 15  # 2*7+1


def test_solution_exists():
    result = generate_maze(5, 5, seed=42)
    assert result.solution is not None
    assert len(result.solution) > 0


def test_solution_starts_and_ends_correctly():
    result = generate_maze(5, 5, seed=42)
    start, end = result.solution[0], result.solution[-1]
    # start debe ser (1,0) o (0,1) — entrada en borde superior-izquierdo
    # end debe ser en borde inferior-derecho
    assert start[0] <= 2 and start[1] <= 2
    assert end[0] >= 8 and end[1] >= 8


def test_svg_is_valid_html():
    result = generate_maze(5, 5, seed=42)
    assert "<svg" in result.svg_html
    assert "</svg>" in result.svg_html
    assert 'viewBox' in result.svg_html


def test_svg_contains_path_for_solution():
    result = generate_maze(5, 5, seed=42)
    assert 'class="solution"' in result.svg_html


def test_reproducible_with_seed():
    r1 = generate_maze(6, 6, seed=99)
    r2 = generate_maze(6, 6, seed=99)
    assert r1.grid == r2.grid


def test_large_maze():
    result = generate_maze(12, 12, seed=1)
    assert len(result.solution) > 10
