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


def test_generate_newsletter_content_aligns_payroll_topic_sections():
    content = generate_newsletter_content([
        _article(title="Key Features of Kelly Payroll Services", url="https://example.com/payroll")
    ])
    lowered = content.lower()
    assert "payroll" in lowered
    assert "video call" not in lowered


def test_generate_newsletter_content_selects_best_feature_from_top_candidates():
    articles = [
        _article(title="Market update", url="https://example.com/market", summary="General recap"),
        _article(
            title="Key Features of Kelly Payroll Services",
            url="https://example.com/payroll",
            summary="Payroll automation and tax remittance for small business owners",
        ),
        _article(title="Town notice", url="https://example.com/town", summary="Local bulletin"),
    ]
    content = generate_newsletter_content(articles)
    assert "https://example.com/payroll" in content
    assert "payroll confidence" in content.lower()


def test_generate_newsletter_content_deprioritizes_announcement_headlines():
    articles = [
        _article(
            title="Jane Doe appointed CEO in quarterly earnings update",
            url="https://example.com/ceo",
            summary="Corporate announcement and board update",
        ),
        _article(
            title="Simple payroll checklist for local shops",
            url="https://example.com/checklist",
            summary="Payroll deductions and tax remittance steps for small business",
        ),
    ]
    content = generate_newsletter_content(articles)
    assert "https://example.com/checklist" in content
    assert "payroll" in content.lower()


def test_generate_newsletter_content_prioritizes_digital_confidence_theme():
    articles = [
        _article(
            title="Regional board quarterly update",
            url="https://example.com/board",
            summary="Corporate earnings and dividend notes",
        ),
        _article(
            title="Community digital confidence workshop helps bridge the digital divide",
            url="https://example.com/confidence",
            summary="Local digital advocacy and inclusion support for neighbours",
        ),
    ]
    content = generate_newsletter_content(articles)
    assert "https://example.com/confidence" in content


def test_generate_newsletter_content_rotates_among_top_scored_by_day():
    articles = [
        _article(
            title="Community digital confidence workshop",
            url="https://example.com/confidence",
            summary="Bridge the digital divide with local tech support",
        ),
        _article(
            title="Simple payroll checklist for local shops",
            url="https://example.com/payroll",
            summary="Payroll and tax remittance steps",
        ),
        _article(
            title="How to avoid phishing scams",
            url="https://example.com/cyber",
            summary="Cybersecurity basics for families and small business",
        ),
    ]

    day_one = generate_newsletter_content(articles, edition_date=date(2026, 4, 1))
    day_two = generate_newsletter_content(articles, edition_date=date(2026, 4, 2))

    links = {
        "https://example.com/confidence": ("https://example.com/confidence" in day_one, "https://example.com/confidence" in day_two),
        "https://example.com/payroll": ("https://example.com/payroll" in day_one, "https://example.com/payroll" in day_two),
        "https://example.com/cyber": ("https://example.com/cyber" in day_one, "https://example.com/cyber" in day_two),
    }
    # Different days should rotate to a different feature option.
    assert day_one != day_two
    assert any(pair[0] != pair[1] for pair in links.values())


def test_generate_newsletter_content_expands_scan_for_practical_alignment():
    articles = [
        _article(title="Board appoints new CEO", url="https://example.com/a1", summary="Quarterly earnings update"),
        _article(title="Dividend announcement", url="https://example.com/a2", summary="Investor relations"),
        _article(title="Market recap", url="https://example.com/a3", summary="Regional market commentary"),
        _article(title="Executive transition update", url="https://example.com/a4", summary="Corporate governance note"),
        _article(
            title="Digital confidence clinic helps neighbours bridge the digital divide",
            url="https://example.com/practical",
            summary="Local digital advocacy and online safety support",
        ),
    ]

    content = generate_newsletter_content(articles, edition_date=date(2026, 4, 1))
    assert "https://example.com/practical" in content


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
