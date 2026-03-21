"""
Tests for filter.py
"""

import re
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from filter import is_relevant, filter_articles


# ── Helpers ───────────────────────────────────────────────────────────────────

def _article(title="", summary="", source="Test Feed", url="https://example.com/1"):
    return {"title": title, "summary": summary, "source": source, "url": url, "published": None}


# ── is_relevant ───────────────────────────────────────────────────────────────

def test_is_relevant_matches_senior_keyword_in_title():
    article = _article(title="New accessibility tools for seniors in 2024")
    assert is_relevant(article) is True


def test_is_relevant_matches_smb_keyword_in_summary():
    article = _article(summary="This cloud platform helps small business owners automate payroll.")
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
        _article(title="Ontario entrepreneur wins award"),
        _article(title="New gaming console released"),
        _article(title="Telemedicine for seniors in Canada"),
    ]
    result = filter_articles(articles)
    titles = [a["title"] for a in result]
    assert "Telemedicine for seniors in Canada" in titles
    assert "Ontario entrepreneur wins award" not in titles
    assert "New gaming console released" not in titles


def test_filter_articles_respects_max_articles():
    articles = [
        _article(title=f"Ontario seniors SMB news {i}", url=f"https://example.com/{i}")
        for i in range(50)
    ]
    result = filter_articles(articles, max_articles=5)
    assert len(result) == 5


def test_filter_articles_requires_senior_relevance():
    articles = [
        _article(title="Ontario SMB grant update", url="https://example.com/1"),
        _article(title="Accessibility tools for seniors in Ontario", url="https://example.com/2"),
        _article(title="Cloud accounting for small business", url="https://example.com/3"),
    ]

    result = filter_articles(articles, max_articles=2)
    titles = [a["title"] for a in result]

    assert titles == ["Accessibility tools for seniors in Ontario"]


def test_filter_articles_returns_empty_when_nothing_relevant():
    articles = [
        _article(title="Soccer match highlights"),
        _article(title="New movie release review"),
    ]
    result = filter_articles(articles)
    assert result == []


def test_filter_articles_handles_empty_input():
    assert filter_articles([]) == []
