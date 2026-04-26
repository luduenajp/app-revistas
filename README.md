# App Revistas — Magazine Factory

A Python tool for generating children's and adult puzzle magazines as print-ready PDFs.

## Project Structure

```
src/
  generators/   # Activity generators (maze, word search, sudoku, etc.)
  renderers/    # HTML page assembler + Playwright PDF exporter
  templates/    # Jinja2 HTML templates
output/         # Generated PDFs (gitignored)
tests/          # pytest tests
demo/           # Demo scripts
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Usage

Coming soon.
