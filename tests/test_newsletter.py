"""
Tests for newsletter.py
"""

import sys
import os
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from newsletter import render_newsletter, save_newsletter

# Use the real templates directory
_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _article(title="Test Article", url="https://example.com/1", summary="A test summary.",
              source="CBC Technology", published=None):
    return {
        "title": title,
        "url": url,
        "summary": summary,
        "source": source,
        "published": published,
    }


# ── render_newsletter ─────────────────────────────────────────────────────────

def test_render_newsletter_contains_title():
    html = render_newsletter([], title="My Newsletter", templates_dir=_TEMPLATES_DIR)
    assert "My Newsletter" in html


def test_render_newsletter_contains_edition_date():
    edition = date(2024, 10, 7)
    html = render_newsletter([], edition_date=edition, templates_dir=_TEMPLATES_DIR)
    assert "October 7, 2024" in html


def test_render_newsletter_renders_article_title_and_link():
    articles = [_article(title="Ontario Grant Program", url="https://example.com/grant")]
    html = render_newsletter(articles, templates_dir=_TEMPLATES_DIR)
    assert "Ontario Grant Program" in html
    assert "https://example.com/grant" in html


def test_render_newsletter_renders_article_summary():
    articles = [_article(summary="Seniors benefit from new digital tools in Ontario.")]
    html = render_newsletter(articles, templates_dir=_TEMPLATES_DIR)
    assert "Seniors benefit from new digital tools in Ontario." in html


def test_render_newsletter_shows_no_articles_message_when_empty():
    html = render_newsletter([], templates_dir=_TEMPLATES_DIR)
    assert "No relevant articles found" in html


def test_render_newsletter_groups_by_source():
    articles = [
        _article(title="Story A", source="CBC Technology"),
        _article(title="Story B", url="https://example.com/2", source="TechCrunch"),
    ]
    html = render_newsletter(articles, templates_dir=_TEMPLATES_DIR)
    assert "CBC Technology" in html
    assert "TechCrunch" in html


# ── save_newsletter ───────────────────────────────────────────────────────────

def test_save_newsletter_creates_file(tmp_path):
    html = "<html><body>Test</body></html>"
    edition = date(2024, 10, 7)
    output_file = save_newsletter(html, output_dir=tmp_path, edition_date=edition)
    assert output_file.exists()
    assert output_file.name == "newsletter_2024-10-07.html"
    assert output_file.read_text(encoding="utf-8") == html


def test_save_newsletter_creates_output_dir(tmp_path):
    new_dir = tmp_path / "newsletters" / "2024"
    html = "<html></html>"
    save_newsletter(html, output_dir=new_dir, edition_date=date(2024, 1, 1))
    assert new_dir.exists()
