"""
scraper.py – fetches and parses RSS feeds into a list of article dicts.
"""

import logging
import urllib.request
from datetime import datetime, timezone
from typing import Optional

import feedparser

from config import RSS_FEEDS

# Hard timeout (seconds) for each individual feed HTTP request.
_FEED_TIMEOUT = 10

logger = logging.getLogger(__name__)


def _parse_date(entry: feedparser.FeedParserDict) -> Optional[datetime]:
    """Return a timezone-aware datetime from a parsed feed entry, or None."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            pass
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            pass
    return None


def fetch_feed(feed_config: dict) -> list[dict]:
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
    articles = []

    try:
        try:
            with urllib.request.urlopen(url, timeout=_FEED_TIMEOUT) as response:
                raw = response.read()
        except Exception as exc:
            logger.warning("Could not fetch feed '%s' (%s): %s", name, url, exc)
            return articles

        parsed = feedparser.parse(raw)
        if parsed.bozo and not parsed.entries:
            logger.warning("Feed '%s' returned a malformed response: %s", name, url)
            return articles

        for entry in parsed.entries:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            # Prefer the full content summary; fall back to description
            summary = (
                getattr(entry, "summary", "")
                or getattr(entry, "description", "")
            ).strip()
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


def fetch_all_feeds(feeds: list[dict] | None = None) -> list[dict]:
    """
    Fetch every feed in *feeds* (defaults to RSS_FEEDS from config) and
    return a combined, deduplicated list of article dicts sorted newest-first.
    """
    if feeds is None:
        feeds = RSS_FEEDS

    all_articles: list[dict] = []
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
