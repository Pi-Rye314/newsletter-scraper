"""
Tests for newsletter.py
"""

import sys
import os
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from newsletter import (
    render_newsletter,
    save_newsletter,
    generate_newsletter_content,
)

# Use the real templates directory
_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _article(
    title="Test Article",
    url="https://example.com/1",
    summary="A test summary.",
    source="CBC Technology",
    published=None,
):
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


def test_render_newsletter_renders_feature_story():
    articles = [
        _article(title="Ontario Grant Program", url="https://example.com/grant")
    ]
    html = render_newsletter(articles, templates_dir=_TEMPLATES_DIR)
    assert "Ontario Grant Program" in html
    assert "https://example.com/grant" in html


# ── generate_newsletter_content ───────────────────────────────────────────────


def test_generate_newsletter_content_with_article():
    articles = [
        _article(title="Tech for Seniors", url="https://example.com/tech-seniors")
    ]
    content = generate_newsletter_content(articles)
    assert "Tech for Seniors" in content
    assert "https://example.com/tech-seniors" in content


def test_generate_newsletter_content_no_articles():
    content = generate_newsletter_content([])
    assert "No featured article available" in content


def test_generate_newsletter_content_adds_surrounding_area_reference():
    content = generate_newsletter_content([
        _article(title="Payroll security for small business", url="https://example.com/payroll")
    ])
    assert "Perth County" in content or "Stratford" in content


def test_generate_newsletter_content_keeps_minimum_cyber_actions():
    content = generate_newsletter_content([
        _article(title="Cyber basics", url="https://example.com/cyber")
    ])
    indicators = ["two-factor", "password", "suspicious", "update", "backup", "2fa", "phishing"]
    hits = sum(1 for marker in indicators if marker in content.lower())
    assert hits >= 3


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
