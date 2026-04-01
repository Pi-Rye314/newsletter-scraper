"""Newsletter scraper CLI: fetch, filter, and render a daily tech newsletter."""

import argparse
import logging
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

from filter import filter_articles
from logging_config import setup_logging
from newsletter import render_newsletter, save_newsletter
from scraper import fetch_all_feeds

log_file = setup_logging()
logger = logging.getLogger(__name__)


def _parse_edition_date(value: str) -> date:
    """Parse YYYY-MM-DD input into a date object for deterministic edition generation."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--edition-date must be in YYYY-MM-DD format") from exc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the newsletter scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape RSS feeds and generate a weekly newsletter for seniors "
        "and SMBs in Ontario, Canada.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: python main.py --output output_live\n",
    )
    parser.add_argument(
        "--output",
        default="output",
        metavar="DIR",
        help="Directory where to save the generated HTML newsletter (default: output/)",
    )
    parser.add_argument(
        "--no-filter",
        action="store_true",
        help="Include all fetched articles without applying relevance filters",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the newsletter to stdout instead of saving to disk",
    )
    parser.add_argument(
        "--edition-date",
        type=_parse_edition_date,
        help="Edition date in YYYY-MM-DD format (defaults to today)",
    )
    parser.add_argument(
        "--preview-days",
        type=int,
        default=1,
        metavar="N",
        help="Generate N consecutive editions starting at --edition-date (default: 1)",
    )
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    """Main entry point; returns an exit code."""
    args = parse_args(argv)
    start_time = time.time()

    if args.preview_days < 1:
        logger.error("--preview-days must be 1 or greater")
        return 2
    
    try:
        logger.info("=" * 70)
        logger.info("Newsletter generation started. Log file: %s", log_file)
        logger.info("=" * 70)

        logger.info("[STEP 1/4] Fetching RSS feeds …")
        fetch_start = time.time()
        articles = fetch_all_feeds()
        fetch_time = time.time() - fetch_start
        logger.info("Fetched %d articles in total (%.2fs)", len(articles), fetch_time)

        if not args.no_filter:
            logger.info("[STEP 2/4] Filtering articles for relevance …")
            filter_start = time.time()
            articles = filter_articles(articles)
            filter_time = time.time() - filter_start
            logger.info("Kept %d articles after filtering (%.2fs)", len(articles), filter_time)
        else:
            logger.info("[STEP 2/4] Skipping filter (--no-filter flag set)")

        if not articles:
            logger.warning("No articles matched the filter. The newsletter will be empty.")

        base_edition_date = args.edition_date or date.today()
        logger.info("[STEP 3/4] Generating newsletter content …")

        for offset in range(args.preview_days):
            current_date = base_edition_date + timedelta(days=offset)
            render_start = time.time()
            html = render_newsletter(articles, edition_date=current_date)
            render_time = time.time() - render_start
            logger.debug("Generated HTML content for %s (%.2fs)", current_date.isoformat(), render_time)

            if args.dry_run:
                logger.info("[DRY-RUN] Outputting edition for %s", current_date.isoformat())
                print(f"\n===== NEWSLETTER PREVIEW: {current_date.isoformat()} =====\n")
                print(html)
                continue

            logger.info("[STEP 4/4] Saving newsletter to disk (%s) …", current_date.isoformat())
            save_start = time.time()
            output_file = save_newsletter(html, output_dir=args.output, edition_date=current_date)
            save_time = time.time() - save_start
            logger.info("Newsletter saved to %s (%.2fs)", output_file, save_time)
        
        total_time = time.time() - start_time
        logger.info("=" * 70)
        logger.info("Newsletter generation completed successfully in %.2fs", total_time)
        logger.info("=" * 70)
        return 0
        
    except Exception as exc:
        logger.error("Fatal error during newsletter generation: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(run())
