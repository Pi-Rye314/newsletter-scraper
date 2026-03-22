from pathlib import Path
import logging
import traceback

status_file = Path("c:/Users/truec/Desktop/newsletter-scraper/live_run_status.txt")
output_dir = Path("c:/Users/truec/Desktop/newsletter-scraper/output_live")

try:
    from main import run

    logging.disable(logging.CRITICAL)
    code = run(["--output", str(output_dir)])
    files = sorted(str(p) for p in output_dir.glob("newsletter_*.html"))
    status_file.write_text(f"code={code}\nfiles={files}\n", encoding="utf-8")
except Exception:
    status_file.write_text(traceback.format_exc(), encoding="utf-8")
