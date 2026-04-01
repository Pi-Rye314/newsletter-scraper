"""
main.py – CLI entry point for the newsletter scraper.

Usage:
    python main.py [--output OUTPUT_DIR] [--no-filter] [--dry-run]
"""

import argparse
import logging
import sys
import time
from datetime import date
from pathlib import Path

from filter import filter_articles
from newsletter import render_newsletter, save_newsletter
from scraper import fetch_all_feeds

def _setup_logging():
    """Configure logging with both console and file output."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"newsletter_{date.today().isoformat()}.log"
    
    # Format string for detailed logging
    log_format = "%(asctime)s  %(name)-20s  %(levelname)-8s  %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Root logger config
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    
    # File handler (DEBUG and above)
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_format, datefmt=date_format)
    file_handler.setFormatter(file_formatter)
    
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    return log_file

log_file = _setup_logging()
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
    start_time = time.time()
    
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

        logger.info("[STEP 3/4] Generating newsletter content …")
        render_start = time.time()
        edition_date = date.today()
        html = render_newsletter(articles, edition_date=edition_date)
        render_time = time.time() - render_start
        logger.debug("Generated HTML content (%.2fs)", render_time)

        if args.dry_run:
            logger.info("[DRY-RUN] Outputting to stdout instead of saving")
            print(html)
            return 0

        logger.info("[STEP 4/4] Saving newsletter to disk …")
        save_start = time.time()
        output_file = save_newsletter(html, output_dir=args.output, edition_date=edition_date)
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
