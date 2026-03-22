"""
scraper.py – fetches and parses RSS feeds into a list of article dicts.
"""

import logging
import re
import urllib.request
from datetime import datetime, timezone
from html import unescape
from typing import Any, Optional

import feedparser  # type: ignore[import-not-found]

from config import RSS_FEEDS

# Hard timeout (seconds) for each individual feed HTTP request.
_FEED_TIMEOUT = 10

logger = logging.getLogger(__name__)

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
_WHITESPACE_RE = re.compile(r"\s+")


def _clean_text(value: str) -> str:
    """Return plain text safe for HTML rendering from messy feed fields."""
    if not value:
        return ""

    text = unescape(str(value))
    text = _HTML_TAG_RE.sub(" ", text)
    text = _CONTROL_CHAR_RE.sub("", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def _parse_date(entry: Any) -> Optional[datetime]:  # feedparser.FeedParserDict lacks stubs
    """Return a timezone-aware datetime from a parsed feed entry, or None."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:  # type: ignore[attr-defined]
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)  # type: ignore[attr-defined]
        except (TypeError, ValueError):
            pass
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:  # type: ignore[attr-defined]
        try:
            return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)  # type: ignore[attr-defined]
        except (TypeError, ValueError):
            pass
    return None


def fetch_feed(feed_config: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Fetch a single RSS feed and return a list of normalised article dicts.

    Each article dict has:
        - title (str)
        - url   (str)
        - summary (str)
        - published (datetime | None)
        - source (str)  – human-readable feed name
    """
    name = feed_config.get("name", "Unknown")
    url = feed_config.get("url", "")
    articles: list[dict[str, Any]] = []

    try:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; NewsletterBot/1.0; +https://github.com/Pi-Rye314/newsletter-scraper)"},
            )
            with urllib.request.urlopen(req, timeout=_FEED_TIMEOUT) as response:
                raw = response.read()
        except Exception as exc:
            logger.warning("Could not fetch feed '%s' (%s): %s", name, url, exc)
            return articles

        parsed = feedparser.parse(raw)  # type: ignore[attr-defined]
        if parsed.bozo and not parsed.entries:  # type: ignore[attr-defined]
            logger.warning("Feed '%s' returned a malformed response: %s", name, url)
            return articles

        for entry in parsed.entries:  # type: ignore[attr-defined]
            title = _clean_text(getattr(entry, "title", ""))  # type: ignore[arg-type]
            link = getattr(entry, "link", "").strip()  # type: ignore[arg-type]
            # Prefer the full content summary; fall back to description
            summary = _clean_text(
                getattr(entry, "summary", "")  # type: ignore[arg-type]
                or getattr(entry, "description", "")  # type: ignore[arg-type]
            )
            published = _parse_date(entry)

            if not title or not link:
                continue

            articles.append(
                {
                    "title": title,
                    "url": link,
                    "summary": summary,
                    "published": published,
                    "source": name,
                }
            )

        logger.info("Fetched %d articles from '%s'", len(articles), name)
    except Exception as exc:  # pragma: no cover – network errors vary widely
        logger.error("Failed to fetch feed '%s' (%s): %s", name, url, exc)

    return articles


def fetch_all_feeds(feeds: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:  # type: ignore[misc]
    """
    Fetch every feed in *feeds* (defaults to RSS_FEEDS from config) and
    return a combined, deduplicated list of article dicts sorted newest-first.
    """
    if feeds is None:
        feeds = RSS_FEEDS  # type: ignore[assignment]

    all_articles: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for feed_config in feeds:
        for article in fetch_feed(feed_config):
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                all_articles.append(article)

    # Sort newest-first; articles without a date go to the end
    all_articles.sort(
        key=lambda a: a["published"] or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )

    logger.info("Total unique articles fetched: %d", len(all_articles))
    return all_articles
