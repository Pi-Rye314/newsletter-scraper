"""
filter.py – keeps only articles relevant to seniors and SMBs in Ontario, Canada.
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Iterable

from config import (
    ALL_KEYWORDS,
    MAX_ARTICLES,
    ONTARIO_KEYWORDS,
    SENIOR_KEYWORDS,
    SMB_KEYWORDS,
    NEGATIVE_KEYWORDS,
)

# Articles older than this many days are dropped regardless of relevance.
_MAX_AGE_DAYS = 14


def _make_patterns(keywords: list[str]) -> list[re.Pattern]:
    """Compile keyword list into word-boundary-aware regex patterns."""
    return [re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE) for kw in keywords]


# Pre-compile keyword patterns for speed
_PATTERNS = _make_patterns(ALL_KEYWORDS)
_SENIOR_PATTERNS = _make_patterns(SENIOR_KEYWORDS)
_SMB_PATTERNS = _make_patterns(SMB_KEYWORDS)
_AUDIENCE_PATTERNS = _make_patterns(SENIOR_KEYWORDS + SMB_KEYWORDS)
_ONTARIO_PATTERNS = _make_patterns(ONTARIO_KEYWORDS)
_NEGATIVE_PATTERNS = _make_patterns(NEGATIVE_KEYWORDS)


def _text_matches(text: str, patterns: list[re.Pattern]) -> bool:
    """Return True if *text* contains at least one keyword pattern."""
    for pattern in patterns:
        if pattern.search(text):
            return True
    return False


def is_relevant(article: dict, patterns: list[re.Pattern] | None = None) -> bool:
    """
    Return True if the article is relevant to the target audience.

    Relevance is determined by checking the article title and summary
    against the combined keyword list (seniors, SMBs, Ontario).
    """
    if patterns is None:
        patterns = _PATTERNS

    combined_text = " ".join(
        [
            article.get("title", ""),
            article.get("summary", ""),
        ]
    )
    return _text_matches(combined_text, patterns)


def _is_fresh(article: dict) -> bool:
    """Return True if the article was published within _MAX_AGE_DAYS, or has no date."""
    published = article.get("published")
    if published is None:
        return True
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=_MAX_AGE_DAYS)
    return published >= cutoff


def filter_articles(
    articles: Iterable[dict],
    patterns: list[re.Pattern] | None = None,
    max_articles: int = MAX_ARTICLES,
) -> list[dict]:
    """
    Filter *articles* to those relevant to the target audience and cap the
    result at *max_articles*.

    An article must satisfy ALL of:
      1. Does NOT match any NEGATIVE_KEYWORDS.
      2. Matches at least one SENIOR_KEYWORDS OR SMB_KEYWORDS term
         (audience relevance – the Stonetown Digital Dispatch serves seniors
         and small-business owners in St. Marys, Ontario).
      3. Matches at least one ONTARIO_KEYWORDS term (Canadian/Ontario context),
         OR comes from a curated feed (source tag is trusted).
      4. Published within _MAX_AGE_DAYS (or undated) – unless from a trusted feed.

    Articles are assumed to arrive newest-first (as produced by scraper.py).
    """
    # Feeds curated for our audience; freshness and Ontario gates are waived.
    _TRUSTED_FEEDS = {
        "CARP",
        "IT World Canada",
        "IT Business Canada",
        "BetaKit",
        "Small Business Trends",
    }

    relevant = []
    for a in articles:
        # 1. Drop articles that match negative keywords
        if is_relevant(a, _NEGATIVE_PATTERNS):
            continue

        # 2. Must match senior OR SMB audience keywords
        if not is_relevant(a, _AUDIENCE_PATTERNS):
            continue

        from_trusted_feed = a.get("source") in _TRUSTED_FEEDS
        # 3 & 4. Trusted feeds: always include. General feeds: fresh + Ontario.
        if from_trusted_feed or (_is_fresh(a) and is_relevant(a, _ONTARIO_PATTERNS)):
            relevant.append(a)

    return relevant[:max_articles]
