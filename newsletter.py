"""
newsletter.py – renders a list of filtered articles into an HTML newsletter.
"""

from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import NEWSLETTER_SUBTITLE, NEWSLETTER_TITLE

# Locate the templates directory relative to this file
_TEMPLATES_DIR = Path(__file__).parent / "templates"


def _build_jinja_env(templates_dir: Path | None = None) -> Environment:
    """Create and return a configured Jinja2 Environment."""
    directory = str(templates_dir or _TEMPLATES_DIR)
    return Environment(
        loader=FileSystemLoader(directory),
        autoescape=select_autoescape(["html"]),
    )


def render_newsletter(
    articles: list[dict],
    edition_date: date | None = None,
    title: str = NEWSLETTER_TITLE,
    subtitle: str = NEWSLETTER_SUBTITLE,
    templates_dir: Path | None = None,
) -> str:
    """
    Render the newsletter HTML from *articles* and return it as a string.

    Parameters
    ----------
    articles:
        List of article dicts (as produced by scraper / filter modules).
    edition_date:
        The edition date shown in the header; defaults to today.
    title / subtitle:
        Newsletter branding strings.
    templates_dir:
        Override the template directory (useful in tests).
    """
    if edition_date is None:
        edition_date = date.today()

    env = _build_jinja_env(templates_dir)
    template = env.get_template("newsletter.html")

    # Group articles by source so section headings make sense in the template
    articles_by_source: list[dict] = sorted(
        articles, key=lambda a: a.get("source", "")
    )

    html = template.render(
        title=title,
        subtitle=subtitle,
        edition_date=edition_date.strftime(f"%B {edition_date.day}, %Y"),
        articles=articles_by_source,
    )
    return html


def save_newsletter(
    html: str,
    output_dir: str | Path = "output",
    edition_date: date | None = None,
) -> Path:
    """
    Save *html* to a file inside *output_dir* and return the file path.

    The filename format is ``newsletter_YYYY-MM-DD.html``.
    """
    if edition_date is None:
        edition_date = date.today()

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = output_path / f"newsletter_{edition_date.isoformat()}.html"
    filename.write_text(html, encoding="utf-8")
    return filename
