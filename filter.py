"""Filter module: gate articles by keyword relevance, freshness, and regional focus.

Provides filtering logic for a specialized audience (seniors and SMBs) in Ontario,
with support for trusted feeds, stale article pruning, and audience-specific gatekeeping.
"""

import logging
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

logger = logging.getLogger(__name__)

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
        "CanadianSME",
        "Financial Post",
        "BetaKit",
        "Small Business Trends",
    }

    articles_list = list(articles)
    relevant = []
    filter_stats = {
        "negative_keywords": 0,
        "not_audience": 0,
        "stale": 0,
        "no_ontario": 0,
        "passed": 0,
    }
    
    logger.debug(f"Starting filter on {len(articles_list)} articles (max output: {max_articles})")

    for a in articles_list:
        title = a.get("title", "")[:60]  # Truncate for logging
        source = a.get("source", "Unknown")
        
        # 1. Drop articles that match negative keywords
        if is_relevant(a, _NEGATIVE_PATTERNS):
            filter_stats["negative_keywords"] += 1
            logger.debug(f"[FILTERED] Negative keywords: {source} - {title}")
            continue

        # 2. Must match senior OR SMB audience keywords
        if not is_relevant(a, _AUDIENCE_PATTERNS):
            filter_stats["not_audience"] += 1
            logger.debug(f"[FILTERED] Not audience-relevant: {source} - {title}")
            continue

        from_trusted_feed = a.get("source") in _TRUSTED_FEEDS
        
        # 3 & 4. Trusted feeds: always include. General feeds: fresh + Ontario.
        if not from_trusted_feed:
            if not _is_fresh(a):
                filter_stats["stale"] += 1
                logger.debug(f"[FILTERED] Stale (>{_MAX_AGE_DAYS}d): {source} - {title}")
                continue
                
            if not is_relevant(a, _ONTARIO_PATTERNS):
                filter_stats["no_ontario"] += 1
                logger.debug(f"[FILTERED] No Ontario context: {source} - {title}")
                continue
        
        filter_stats["passed"] += 1
        logger.debug(f"[PASSED] {source} - {title}")
        relevant.append(a)

    # Log summary
    logger.info(
        f"Filtering summary: passed={filter_stats['passed']}, "
        f"negative={filter_stats['negative_keywords']}, "
        f"not_audience={filter_stats['not_audience']}, "
        f"stale={filter_stats['stale']}, "
        f"no_ontario={filter_stats['no_ontario']}"
    )
    
    result = relevant[:max_articles]
    if len(relevant) > max_articles:
        logger.info(f"Capped output to {max_articles} articles (removed {len(relevant) - max_articles} from bottom)")
    
    return result
