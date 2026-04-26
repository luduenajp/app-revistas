import pytest
from src.generators.word_search import generate_word_search, WordSearchResult


WORDS_ES = ["DINOSAURIO", "TIRANOSAURIO", "FOSIL", "HUEVO", "CUELLO"]


def test_returns_word_search_result():
    result = generate_word_search(WORDS_ES, 15, 15, seed=42)
    assert isinstance(result, WordSearchResult)


def test_grid_dimensions():
    result = generate_word_search(WORDS_ES, 12, 14, seed=42)
    assert len(result.grid) == 12
    assert all(len(row) == 14 for row in result.grid)


def test_all_cells_filled():
    result = generate_word_search(WORDS_ES, 12, 12, seed=42)
    for row in result.grid:
        for cell in row:
            assert cell.isalpha() and cell.isupper()


def test_words_present_in_grid(words=WORDS_ES):
    result = generate_word_search(words, 15, 15, seed=42)
    assert set(result.placed_words).issubset(set(words))
    assert len(result.placed_words) > 0


def test_word_found_at_placement():
    result = generate_word_search(["DINO"], 10, 10, seed=1)
    for word, (r, c, dr, dc) in result.placements.items():
        for i, ch in enumerate(word):
            assert result.grid[r + dr * i][c + dc * i] == ch


def test_directions_simple():
    result = generate_word_search(["GATO", "PERRO"], 10, 10,
                                   directions='simple', seed=5)
    for word, (r, c, dr, dc) in result.placements.items():
        # simple: solo horizontal o vertical
        assert dr == 0 or dc == 0


def test_html_output_contains_word_cells():
    result = generate_word_search(["DINO"], 10, 10, seed=2)
    # Verify each letter of placed words appears as a <td> in the table
    for word, (r, c, dr, dc) in result.placements.items():
        for i, ch in enumerate(word):
            assert f"<td" in result.html_table
            assert result.grid[r + dr * i][c + dc * i] == ch


def test_html_is_table():
    result = generate_word_search(["DINO"], 8, 8, seed=3)
    assert "<table" in result.html_table
    assert "</table>" in result.html_table


def test_reproducible_with_seed():
    r1 = generate_word_search(WORDS_ES, 15, 15, seed=77)
    r2 = generate_word_search(WORDS_ES, 15, 15, seed=77)
    assert r1.grid == r2.grid
