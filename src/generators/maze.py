from dataclasses import dataclass
from mazelib import Maze
from mazelib.generate.BacktrackingGenerator import BacktrackingGenerator
from mazelib.solve.BacktrackingSolver import BacktrackingSolver


@dataclass
class MazeResult:
    grid: list[list[int]]   # 2D array: 1=wall, 0=path
    solution: list[tuple]   # Lista de (row, col) desde entrada a salida
    svg_html: str           # SVG embebible como string


def generate_maze(rows: int, cols: int, seed: int | None = None) -> MazeResult:
    m = Maze(seed=seed)
    m.generator = BacktrackingGenerator(rows, cols)
    m.generate()

    grid = m.grid
    num_rows, num_cols = grid.shape

    # Place entrance at top-left: open the wall above the first open cell in row 1
    entry_col = next((c for c in range(num_cols) if grid[1][c] == 0), None)
    if entry_col is None:
        raise ValueError("No open cell found in row 1 — maze generation failed")
    m.start = (0, entry_col)
    m.grid[0][entry_col] = 0

    # Place exit at bottom-right: open the wall below the last open cell in last inner row
    exit_col = next((c for c in range(num_cols - 1, -1, -1) if grid[num_rows - 2][c] == 0), None)
    if exit_col is None:
        raise ValueError("No open cell found in last inner row — maze generation failed")
    m.end = (num_rows - 1, exit_col)
    m.grid[num_rows - 1][exit_col] = 0

    m.solver = BacktrackingSolver()
    m.solve()

    grid_list = m.grid.tolist()
    solution = list(m.solutions[0]) if m.solutions else []
    if solution:
        solution = [(0, entry_col)] + solution + [(num_rows - 1, exit_col)]

    svg_html = _render_svg(grid_list, solution, cell_px=20)
    return MazeResult(grid=grid_list, solution=solution, svg_html=svg_html)


def _render_svg(grid: list[list[int]], solution: list[tuple], cell_px: int = 20) -> str:
    rows = len(grid)
    cols = len(grid[0])
    w = cols * cell_px
    h = rows * cell_px

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" style="display:block;max-width:100%;">'
    ]

    # Fondo blanco
    lines.append(f'<rect width="{w}" height="{h}" fill="white"/>')

    # Paredes
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                x, y = c * cell_px, r * cell_px
                lines.append(
                    f'<rect x="{x}" y="{y}" width="{cell_px}" height="{cell_px}" fill="#222"/>'
                )

    # Solución (línea punteada, oculta por defecto)
    if solution:
        points = " ".join(
            f"{c * cell_px + cell_px // 2},{r * cell_px + cell_px // 2}"
            for r, c in solution
        )
        lines.append(
            f'<polyline class="solution" points="{points}" '
            f'fill="none" stroke="#e74c3c" stroke-width="2" '
            f'stroke-dasharray="4 2" opacity="0"/>'
        )

    lines.append("</svg>")
    return "\n".join(lines)
