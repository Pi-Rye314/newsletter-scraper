"""
filter.py – keeps only articles relevant to seniors and SMBs in Ontario, Canada.
"""

import re
from typing import Iterable

from config import ALL_KEYWORDS, MAX_ARTICLES, SENIOR_KEYWORDS

# Pre-compile keyword patterns for speed
_PATTERNS = [re.compile(re.escape(kw), re.IGNORECASE) for kw in ALL_KEYWORDS]
_SENIOR_PATTERNS = [re.compile(re.escape(kw), re.IGNORECASE) for kw in SENIOR_KEYWORDS]


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


def filter_articles(
    articles: Iterable[dict],
    patterns: list[re.Pattern] | None = None,
    max_articles: int = MAX_ARTICLES,
) -> list[dict]:
    """
    Filter *articles* to those relevant to the target audience and cap the
    result at *max_articles*.

    Articles are assumed to arrive newest-first (as produced by scraper.py).
    """
    # Senior relevance is mandatory for inclusion.
    relevant = [
        a
        for a in articles
        if is_relevant(a, patterns) and is_relevant(a, _SENIOR_PATTERNS)
    ]
    return relevant[:max_articles]
