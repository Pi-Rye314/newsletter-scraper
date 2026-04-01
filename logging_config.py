"""Logging configuration for the newsletter scraper.

Provides centralized logging setup with both console and file output.
"""

import logging
from datetime import date
from pathlib import Path


def setup_logging(log_dir: str | Path = "logs", prefix: str = "newsletter") -> Path:
    """Configure logging with console (INFO) and file (DEBUG) handlers.

    Args:
        log_dir: Directory where log files are stored. Created if missing.
        prefix: Prefix for log filenames (format: {prefix}_{date}.log).

    Returns:
        Path to the log file created for today's date.
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"{prefix}_{date.today().isoformat()}.log"

    # Format string for detailed logging
    log_format = "%(asctime)s  %(name)-20s  %(levelname)-8s  %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Root logger config
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Remove any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

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
