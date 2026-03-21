"""
main.py – CLI entry point for the newsletter scraper.

Usage:
    python main.py [--output OUTPUT_DIR] [--no-filter] [--dry-run]
"""

import argparse
import logging
import sys
from datetime import date
from pathlib import Path

from filter import filter_articles
from newsletter import render_newsletter, save_newsletter
from scraper import fetch_all_feeds

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape RSS feeds and generate a weekly newsletter for seniors "
        "and SMBs in Ontario, Canada."
    )
    parser.add_argument(
        "--output",
        default="output",
        help="Directory where the generated HTML newsletter is saved (default: output/).",
    )
    parser.add_argument(
        "--no-filter",
        action="store_true",
        help="Include all fetched articles without keyword filtering.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the newsletter to stdout instead of saving to disk.",
    )
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    """Main entry point; returns an exit code."""
    args = parse_args(argv)

    logger.info("Fetching RSS feeds …")
    articles = fetch_all_feeds()
    logger.info("Fetched %d articles in total.", len(articles))

    if not args.no_filter:
        articles = filter_articles(articles)
        logger.info("Kept %d articles after filtering.", len(articles))

    if not articles:
        logger.warning("No articles matched the filter. The newsletter will be empty.")

    edition_date = date.today()
    html = render_newsletter(articles, edition_date=edition_date)

    if args.dry_run:
        print(html)
        return 0

    output_file = save_newsletter(html, output_dir=args.output, edition_date=edition_date)
    logger.info("Newsletter saved to %s", output_file)
    return 0


if __name__ == "__main__":
    sys.exit(run())
