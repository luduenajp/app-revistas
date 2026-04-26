# Diseño: Actividad "Unir con Puntos"

**Fecha:** 2026-04-26  
**Estado:** Aprobado

## Resumen

Agregar un tercer tipo de actividad al generador de revistas infantiles: "unir con puntos" (connect-the-dots). El jugador une puntos numerados en orden para revelar una figura. Se genera un PDF A4 con una figura por página.

## Decisiones de diseño

| Pregunta | Decisión |
|---|---|
| Fuente de figuras | Biblioteca de PNGs de siluetas (`src/shapes/`) |
| Generación de puntos | Trazar contorno del PNG con `skimage.measure.find_contours`, samplear N puntos equidistantes por longitud de arco |
| Dificultad | Dos niveles: `easy` (15 puntos), `hard` (28 puntos), ambos del mismo contorno |
| Solución en PDF | No se incluye |
| Layout | Una figura por página, centrada, título y subtítulo arriba |
| Estilo de puntos | Círculo relleno `r=5` en `color_primary`, número al costado en `color_text` |

## Arquitectura

Sigue el patrón existente: generator → renderer → template → PDF.

### Archivos nuevos

| Archivo | Rol |
|---|---|
| `src/shapes/` | Directorio con PNGs de siluetas (negro sobre blanco) |
| `src/shapes/dinosaurio.png` | Silueta inicial |
| `src/shapes/estrella.png` | Silueta inicial |
| `src/shapes/cohete.png` | Silueta inicial |
| `src/shapes/corazon.png` | Silueta inicial |
| `src/generators/dot_connect.py` | Generator principal |
| `src/templates/dot_connect_activity.html.j2` | Template Jinja2 |

### Archivos modificados

| Archivo | Cambio |
|---|---|
| `src/renderers/html_page.py` | Agrega `render_dot_connect_page()` |
| `demo/demo_dinos.py` | Agrega tercera página al demo |
| `requirements.txt` | Agrega `scikit-image` |

## Interfaz pública del generator

```python
@dataclass
class DotConnectResult:
    dots: list[tuple[float, float]]  # coordenadas escaladas al SVG (x, y)
    label: str                        # nombre de la figura (ej. "dinosaurio")
    difficulty: str                   # 'easy' | 'hard'
    svg_html: str                     # SVG embebible como string

def generate_dot_connect(
    figure: str,              # nombre del PNG en src/shapes/ sin extensión
    difficulty: str = "easy", # 'easy' = 15 puntos | 'hard' = 28 puntos
    width_px: int = 400,
    height_px: int = 400,
) -> DotConnectResult:
    ...
```

## Flujo interno del generator

1. Resolver ruta: `src/shapes/{figure}.png`
2. Cargar con `Pillow` → convertir a escala de grises → binarizar (umbral 128)
3. `skimage.measure.find_contours(binary, level=0.5)` → lista de contornos
4. Seleccionar el contorno más largo (silueta principal, ignorar huecos)
5. Calcular longitud de arco acumulada a lo largo del contorno
6. Samplear N puntos equidistantes mediante interpolación lineal
7. Escalar coordenadas al espacio `width_px × height_px`
8. Generar SVG con `_render_svg(dots, width_px, height_px)`

### SVG rendering

- Fondo blanco `<rect>`
- Por cada punto `(x, y)` con índice `i`:
  - `<circle cx="{x}" cy="{y}" r="5" fill="{color_primary}"/>`
  - Número `i+1` a la derecha del punto (`x+9`), o a la izquierda si `x > width_px * 0.8`
- Sin líneas de solución

## Renderer

```python
# src/renderers/html_page.py
def render_dot_connect_page(
    dot_svg: str,
    title: str = "¡Uní los puntos!",
    subtitle: str = "",
    style: dict | None = None,
) -> str:
    ctx = {**(style or {}), "title": title, "subtitle": subtitle, "dot_svg": dot_svg}
    return _env.get_template("dot_connect_activity.html.j2").render(**ctx)
```

## Template

`dot_connect_activity.html.j2` hereda `base.html.j2`. Estructura:
- Título (`color_primary`, bold)
- Subtítulo (`color_text`, opacidad reducida — igual que los templates existentes)
- SVG centrado con `max-width: 100%`

Sin sección de solución ni palabras a encontrar.

## Demo de uso

```python
# demo/demo_dinos.py (ampliado)
dc = generate_dot_connect("dinosaurio", difficulty="easy")
dc_html = render_dot_connect_page(
    dc.svg_html,
    title="¡Uní los puntos y descubrí el dino!",
    subtitle=f"Empezá por el 1 y seguí en orden. ({len(dc.dots)} puntos)",
    style=STYLE_INFANTIL,
)
pdf3 = export_html_to_pdf(dc_html, OUT / "dinos_puntos.pdf")
```

## Requisitos de los PNGs

- Silueta negra sobre fondo blanco
- Un solo contorno principal (sin partes desconectadas)
- Sin ruido ni bordes difusos
- Tamaño recomendado: 200×200 px o más

## Dependencias nuevas

- `scikit-image` — detección de contornos (`find_contours`)
- `Pillow` — carga y binarización de PNG (probablemente ya instalado)

## Testing

- `tests/test_dot_connect.py`:
  - `generate_dot_connect("estrella", "easy")` retorna 15 puntos
  - `generate_dot_connect("estrella", "hard")` retorna 28 puntos
  - Todos los puntos dentro del bounding box `[0, width_px] × [0, height_px]`
  - `svg_html` contiene los círculos y números correctos
  - Error claro si `figure` no existe en `src/shapes/`
