from pathlib import Path
from playwright.sync_api import sync_playwright


def export_html_to_pdf(html: str, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        page.pdf(
            path=str(output_path),
            width="216mm",
            height="303mm",
            print_background=True,
        )
        browser.close()

    return output_path
