from dataclasses import dataclass
import random
import string


@dataclass
class WordSearchResult:
    grid: list[list[str]]          # 2D de letras mayúsculas
    placed_words: list[str]        # Palabras efectivamente colocadas
    placements: dict[str, tuple]   # word -> (r, c, dr, dc)
    html_table: str                # <table>...</table> embebible


_ALL_DIRS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
_SIMPLE_DIRS = [(0, 1), (1, 0)]  # horizontal derecha, vertical abajo


def generate_word_search(
    words: list[str],
    rows: int,
    cols: int,
    directions: str = 'all',
    seed: int | None = None,
) -> WordSearchResult:
    if directions == 'all':
        dirs = _ALL_DIRS
    elif directions == 'simple':
        dirs = _SIMPLE_DIRS
    else:
        raise ValueError(f"directions must be 'all' or 'simple', got {directions!r}")
    rng = random.Random(seed)

    grid = [[''] * cols for _ in range(rows)]
    placed_words: list[str] = []
    placements: dict[str, tuple] = {}

    sorted_words = sorted([w.upper() for w in words], key=len, reverse=True)

    for word in sorted_words:
        placed = _try_place(grid, word, rows, cols, dirs, rng, attempts=200)
        if placed:
            r, c, dr, dc = placed
            placed_words.append(word)
            placements[word] = (r, c, dr, dc)
            for i, ch in enumerate(word):
                grid[r + dr * i][c + dc * i] = ch

    # Rellenar celdas vacías con letras aleatorias
    for r in range(rows):
        for c in range(cols):
            if not grid[r][c]:
                grid[r][c] = rng.choice(string.ascii_uppercase)

    html_table = _render_html(grid, placements)
    return WordSearchResult(grid, placed_words, placements, html_table)


def _try_place(grid, word, rows, cols, dirs, rng, attempts):
    for _ in range(attempts):
        dr, dc = rng.choice(dirs)
        r = rng.randint(0, rows - 1)
        c = rng.randint(0, cols - 1)
        end_r = r + dr * (len(word) - 1)
        end_c = c + dc * (len(word) - 1)
        if not (0 <= end_r < rows and 0 <= end_c < cols):
            continue
        conflict = False
        for i, ch in enumerate(word):
            cell = grid[r + dr * i][c + dc * i]
            if cell and cell != ch:
                conflict = True
                break
        if not conflict:
            return r, c, dr, dc
    return None


def _render_html(grid: list[list[str]], placements: dict) -> str:
    # Construir set de celdas que pertenecen a palabras (para resaltar en clave)
    solution_cells: set[tuple] = set()
    for word, (r, c, dr, dc) in placements.items():
        for i in range(len(word)):
            solution_cells.add((r + dr * i, c + dc * i))

    rows_html = []
    for ri, row in enumerate(grid):
        cells = []
        for ci, ch in enumerate(row):
            css = ' class="sol"' if (ri, ci) in solution_cells else ''
            cells.append(f"<td{css}>{ch}</td>")
        rows_html.append(f"<tr>{''.join(cells)}</tr>")

    table = (
        '<table class="word-search">'
        + "".join(rows_html)
        + "</table>"
    )

    return table
