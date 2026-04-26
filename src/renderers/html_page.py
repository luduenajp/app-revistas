from pathlib import Path
from jinja2 import Environment, FileSystemLoader

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
_env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)))


def render_maze_page(
    maze_svg: str,
    title: str = "¡Encuentra la salida!",
    subtitle: str = "",
    style: dict | None = None,
) -> str:
    ctx = {**(style or {}), "title": title, "subtitle": subtitle, "maze_svg": maze_svg}
    return _env.get_template("maze_activity.html.j2").render(**ctx)


def render_word_search_page(
    table_html: str,
    words: list[str],
    title: str = "Sopa de Letras",
    subtitle: str = "",
    style: dict | None = None,
) -> str:
    ctx = {**(style or {}), "title": title, "subtitle": subtitle,
           "table_html": table_html, "words": words}
    return _env.get_template("word_search_activity.html.j2").render(**ctx)
