"""
Tests for scraper.py
"""

import sys
import os
from datetime import datetime, timezone
from io import BytesIO
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scraper import _parse_date, fetch_feed, fetch_all_feeds


def _urlopen_mock(data: bytes = b"<rss/>"):
    """Return a context-manager mock for urllib.request.urlopen."""
    @contextmanager
    def _mgr(*args, **kwargs):
        resp = MagicMock()
        resp.read.return_value = data
        yield resp
    return _mgr


# ── _parse_date ──────────────────────────────────────────────────────────────

def _make_entry(**kwargs):
    """Create a simple mock feed entry."""
    entry = MagicMock()
    # Remove all attributes by default
    for attr in ("published_parsed", "updated_parsed", "title", "link", "summary", "description"):
        setattr(entry, attr, None)
    for k, v in kwargs.items():
        setattr(entry, k, v)
    return entry


def test_parse_date_from_published_parsed():
    entry = _make_entry(published_parsed=(2024, 3, 15, 12, 0, 0, 4, 75, 0))
    result = _parse_date(entry)
    assert result == datetime(2024, 3, 15, 12, 0, 0, tzinfo=timezone.utc)


def test_parse_date_from_updated_parsed_fallback():
    entry = _make_entry(
        published_parsed=None,
        updated_parsed=(2024, 6, 1, 8, 30, 0, 5, 153, 0),
    )
    result = _parse_date(entry)
    assert result == datetime(2024, 6, 1, 8, 30, 0, tzinfo=timezone.utc)


def test_parse_date_returns_none_when_no_dates():
    entry = _make_entry(published_parsed=None, updated_parsed=None)
    result = _parse_date(entry)
    assert result is None


# ── fetch_feed ────────────────────────────────────────────────────────────────

def _make_parsed_feed(entries):
    """Build a minimal feedparser result mock."""
    feed = MagicMock()
    feed.bozo = False
    feed.entries = entries
    return feed


def _make_feed_entry(title="Test Article", link="https://example.com/article",
                     summary="A test summary.", published_parsed=None):
    entry = MagicMock()
    entry.title = title
    entry.link = link
    entry.summary = summary
    entry.description = ""
    entry.published_parsed = published_parsed
    entry.updated_parsed = None
    return entry


def test_fetch_feed_returns_articles():
    entry = _make_feed_entry(
        title="Ontario Small Business Grant",
        link="https://example.com/grant",
        summary="A new grant for Ontario SMBs.",
        published_parsed=(2024, 4, 1, 10, 0, 0, 0, 91, 0),
    )
    mock_feed = _make_parsed_feed([entry])

    with patch("scraper.urllib.request.urlopen", _urlopen_mock()), \
         patch("scraper.feedparser.parse", return_value=mock_feed):
        articles = fetch_feed({"name": "Test Feed", "url": "https://example.com/feed"})

    assert len(articles) == 1
    assert articles[0]["title"] == "Ontario Small Business Grant"
    assert articles[0]["source"] == "Test Feed"
    assert articles[0]["url"] == "https://example.com/grant"


def test_fetch_feed_skips_entries_without_title_or_link():
    entry_ok = _make_feed_entry(title="Good Article", link="https://example.com/ok")
    entry_no_title = _make_feed_entry(title="", link="https://example.com/no-title")
    entry_no_link = _make_feed_entry(title="No Link Article", link="")
    mock_feed = _make_parsed_feed([entry_ok, entry_no_title, entry_no_link])

    with patch("scraper.urllib.request.urlopen", _urlopen_mock()), \
         patch("scraper.feedparser.parse", return_value=mock_feed):
        articles = fetch_feed({"name": "Feed", "url": "https://example.com/feed"})

    assert len(articles) == 1
    assert articles[0]["title"] == "Good Article"


def test_fetch_feed_returns_empty_on_bozo_with_no_entries():
    mock_feed = MagicMock()
    mock_feed.bozo = True
    mock_feed.entries = []

    with patch("scraper.urllib.request.urlopen", _urlopen_mock()), \
         patch("scraper.feedparser.parse", return_value=mock_feed):
        articles = fetch_feed({"name": "Bad Feed", "url": "https://example.com/bad"})

    assert articles == []


def test_fetch_feed_returns_empty_on_network_error():
    import socket

    def _raise(*args, **kwargs):
        raise socket.timeout("timed out")

    with patch("scraper.urllib.request.urlopen", _raise):
        articles = fetch_feed({"name": "Slow Feed", "url": "https://example.com/slow"})

    assert articles == []


# ── fetch_all_feeds ───────────────────────────────────────────────────────────

def test_fetch_all_feeds_deduplicates():
    entry = _make_feed_entry(title="Shared Article", link="https://example.com/shared")
    mock_feed = _make_parsed_feed([entry])

    feeds = [
        {"name": "Feed A", "url": "https://a.com/feed"},
        {"name": "Feed B", "url": "https://b.com/feed"},
    ]

    with patch("scraper.urllib.request.urlopen", _urlopen_mock()), \
         patch("scraper.feedparser.parse", return_value=mock_feed):
        articles = fetch_all_feeds(feeds)

    assert len(articles) == 1


def test_fetch_all_feeds_sorts_newest_first():
    entry1 = _make_feed_entry(
        title="Older", link="https://example.com/old",
        published_parsed=(2024, 1, 1, 0, 0, 0, 0, 1, 0),
    )
    entry2 = _make_feed_entry(
        title="Newer", link="https://example.com/new",
        published_parsed=(2024, 6, 1, 0, 0, 0, 0, 153, 0),
    )
    mock_feed = _make_parsed_feed([entry1, entry2])

    with patch("scraper.urllib.request.urlopen", _urlopen_mock()), \
         patch("scraper.feedparser.parse", return_value=mock_feed):
        articles = fetch_all_feeds([{"name": "F", "url": "https://example.com/feed"}])

    assert articles[0]["title"] == "Newer"
    assert articles[1]["title"] == "Older"
