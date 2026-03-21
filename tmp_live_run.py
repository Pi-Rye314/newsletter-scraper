from pathlib import Path
import logging

from main import run

logging.disable(logging.CRITICAL)

output_dir = Path("c:/Users/truec/Desktop/newsletter-scraper/output_live")
status_file = Path("c:/Users/truec/Desktop/newsletter-scraper/live_run_status.txt")

try:
    code = run(["--output", str(output_dir)])
    files = sorted(str(p) for p in output_dir.glob("newsletter_*.html"))
    status_file.write_text(f"code={code}\nfiles={files}\n", encoding="utf-8")
except Exception as exc:
    status_file.write_text(f"error={exc!r}\n", encoding="utf-8")
