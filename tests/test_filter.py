"""
Tests for filter.py
"""

import re
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from filter import is_relevant, filter_articles, _is_fresh


# ── Helpers ───────────────────────────────────────────────────────────────────

def _article(title="", summary="", source="Test Feed", url="https://example.com/1", published=None):
    return {"title": title, "summary": summary, "source": source, "url": url, "published": published}


# ── _is_fresh ────────────────────────────────────────────────────────────────

def test_is_fresh_allows_undated_article():
    assert _is_fresh(_article()) is True


def test_is_fresh_allows_recent_article():
    from datetime import datetime, timedelta, timezone
    recent = datetime.now(tz=timezone.utc) - timedelta(days=3)
    assert _is_fresh(_article(published=recent)) is True


def test_is_fresh_drops_stale_article():
    from datetime import datetime, timedelta, timezone
    old = datetime.now(tz=timezone.utc) - timedelta(days=30)
    assert _is_fresh(_article(published=old)) is False


# ── is_relevant ───────────────────────────────────────────────────────────────

def test_is_relevant_matches_senior_keyword_in_title():
    article = _article(title="New accessibility tools for seniors in 2024")
    assert is_relevant(article) is True


def test_is_relevant_matches_ontario_keyword():
    article = _article(title="Toronto tech summit announces new grants for startups")
    assert is_relevant(article) is True


def test_is_relevant_is_case_insensitive():
    article = _article(title="RETIREMENT planning software review")
    assert is_relevant(article) is True


def test_is_relevant_returns_false_for_unrelated_article():
    article = _article(
        title="New gaming console released this holiday season",
        summary="The latest gaming hardware beats all records in speed and graphics.",
    )
    assert is_relevant(article) is False


def test_is_relevant_uses_custom_patterns():
    custom_patterns = [re.compile(r"quantum", re.IGNORECASE)]
    article_match = _article(title="Quantum computing breakthrough")
    article_miss = _article(title="Ontario senior retirement fund")
    assert is_relevant(article_match, patterns=custom_patterns) is True
    assert is_relevant(article_miss, patterns=custom_patterns) is False


# ── filter_articles ───────────────────────────────────────────────────────────

def test_filter_articles_keeps_relevant_articles():
    articles = [
        _article(title="New gaming console released"),
        # senior + Ontario keyword → kept
        _article(title="Telemedicine for seniors in Canada"),
        # senior but no Ontario keyword, not a trusted senior feed → dropped
        _article(title="Telemedicine for seniors worldwide", source="Test Feed"),
        # senior + trusted feed source → kept even without Ontario keyword
        _article(title="Retirement planning tips", source="CARP"),
    ]
    result = filter_articles(articles)
    titles = [a["title"] for a in result]
    assert "Telemedicine for seniors in Canada" in titles
    assert "Retirement planning tips" in titles
    assert "New gaming console released" not in titles
    assert "Telemedicine for seniors worldwide" not in titles


def test_filter_articles_drops_negative_keywords():
    articles = [
        # Negative keyword in title → dropped
        _article(
            title="Seniors in Ontario Warned of New Phone Scam",
            source="CARP",
            url="https://example.com/1",
        ),
        # Negative keyword in summary → dropped
        _article(
            title="Tech Support Tips for Elders",
            summary="Understanding the risk of phishing attempts.",
            source="CARP",
            url="https://example.com/2",
        ),
        # No negative keywords → kept
        _article(
            title="Ontario Seniors Embrace New Smart Home Tech",
            source="CARP",
            url="https://example.com/3",
        ),
    ]
    result = filter_articles(articles)
    urls = [a["url"] for a in result]
    assert "https://example.com/1" not in urls
    assert "https://example.com/2" not in urls
    assert "https://example.com/3" in urls


def test_filter_articles_respects_max_articles():
    articles = [
        _article(
            title=f"Ontario seniors news {i}", source="CARP", url=f"https://example.com/{i}"
        )
        for i in range(50)
    ]
    result = filter_articles(articles, max_articles=5)
    assert len(result) == 5


def test_filter_articles_requires_senior_relevance():
    articles = [
        _article(title="Ontario SMB grant update", url="https://example.com/1"),
        # senior + Ontario keyword → kept
        _article(title="Accessibility tools for seniors in Ontario", url="https://example.com/2"),
        _article(title="Cloud accounting for small business", url="https://example.com/3"),
    ]

    result = filter_articles(articles, max_articles=5)
    titles = [a["title"] for a in result]

    assert titles == ["Accessibility tools for seniors in Ontario"]


def test_filter_articles_drops_stale_articles():
    from datetime import datetime, timedelta, timezone
    old = datetime.now(tz=timezone.utc) - timedelta(days=30)
    articles = [
        # stale from a general feed → dropped
        _article(title="Ontario seniors retirement news", source="Test Feed", url="https://example.com/1", published=old),
        # stale from a trusted senior feed → kept (freshness waived)
        _article(title="Retirement planning for retirees", source="CARP", url="https://example.com/2", published=old),
        # undated from a general feed → kept (no date ⇒ treated as fresh)
        _article(title="Ontario seniors retirement news", source="Test Feed", url="https://example.com/3", published=None),
    ]
    result = filter_articles(articles)
    urls = [a["url"] for a in result]
    assert "https://example.com/1" not in urls
    assert "https://example.com/2" in urls
    assert "https://example.com/3" in urls


def test_filter_articles_returns_empty_when_nothing_relevant():
    articles = [
        _article(title="Soccer match highlights"),
        _article(title="New movie release review"),
    ]
    result = filter_articles(articles)
    assert result == []


def test_filter_articles_handles_empty_input():
    assert filter_articles([]) == []
