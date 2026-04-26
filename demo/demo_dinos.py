"""
Demo: Genera una página de laberinto y una de sopa de letras
temática dinosaurios para revista infantil.
Salida: output/dinos_laberinto.pdf, output/dinos_sopa.pdf
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path when run directly (python demo/demo_dinos.py)
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.generators.maze import generate_maze
from src.generators.word_search import generate_word_search
from src.renderers.html_page import render_maze_page, render_word_search_page
from src.renderers.pdf_export import export_html_to_pdf

STYLE_INFANTIL = {
    "font_family": "Nunito:wght@400;700;900",
    "font_name": "Nunito",
    "color_primary": "#e74c3c",
    "color_accent": "#f39c12",
    "color_bg": "#fffdf8",
    "color_text": "#2c3e50",
}

PALABRAS_DINOS = [
    "DINOSAURIO", "FOSIL", "HUEVO", "CUELLO",
    "TIRANOSAURIO", "VELOCIRAPTOR", "TRICERATOPS",
    "PTERODACTILO", "ESTEGOSAURIO",
]

OUT = Path("output")


def main():
    # Laberinto
    maze = generate_maze(rows=9, cols=9, seed=42)
    maze_html = render_maze_page(
        maze.svg_html,
        title="¡Ayuda al dino a encontrar su huevo!",
        subtitle="Sigue el camino sin pasar por las paredes.",
        style=STYLE_INFANTIL,
    )
    pdf1 = export_html_to_pdf(maze_html, OUT / "dinos_laberinto.pdf")
    print(f"✓ Laberinto: {pdf1}")

    # Sopa de letras
    ws = generate_word_search(PALABRAS_DINOS, rows=14, cols=14, seed=42)
    ws_html = render_word_search_page(
        ws.html_table,
        words=ws.placed_words,
        title="Sopa de Letras: Dinosaurios",
        subtitle=f"Encontrá las {len(ws.placed_words)} palabras escondidas.",
        style=STYLE_INFANTIL,
    )
    pdf2 = export_html_to_pdf(ws_html, OUT / "dinos_sopa.pdf")
    print(f"✓ Sopa de letras: {pdf2}")


if __name__ == "__main__":
    main()
