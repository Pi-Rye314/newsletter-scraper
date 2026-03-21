# newsletter-scraper

RSS scraping tool that aggregates tech news relevant to seniors and small/medium businesses (SMBs) in Ontario, Canada, and formats the results as a ready-to-host weekly HTML newsletter.

## Features

- Fetches articles from multiple RSS feeds (CBC, Globe and Mail, TechCrunch, Wired, MIT Technology Review, and more)
- Filters articles by keywords relevant to **seniors** (accessibility, retirement, telehealth, …) and **Ontario SMBs** (grants, cloud tools, cybersecurity, e-commerce, …)
- Renders a clean, responsive HTML newsletter using a Jinja2 template
- Saves one `newsletter_YYYY-MM-DD.html` file per run to an `output/` directory

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Generate this week's newsletter and save it to output/
python main.py

# Save to a custom directory
python main.py --output /path/to/newsletters

# Print HTML to stdout instead of saving (useful for piping)
python main.py --dry-run

# Include every fetched article (skip keyword filtering)
python main.py --no-filter
```

The generated file is self-contained HTML that can be opened in any browser or uploaded directly to a static hosting service.

## Project Structure

```
newsletter-scraper/
├── config.py          # RSS feed URLs and keyword lists
├── scraper.py         # Fetches and normalises RSS feed entries
├── filter.py          # Keyword-based relevance filtering
├── newsletter.py      # Renders and saves the HTML newsletter
├── main.py            # CLI entry point
├── templates/
│   └── newsletter.html   # Jinja2 HTML template
├── tests/
│   ├── test_scraper.py
│   ├── test_filter.py
│   └── test_newsletter.py
└── requirements.txt
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Customising

- **Add or remove RSS feeds** – edit the `RSS_FEEDS` list in `config.py`.
- **Tune keyword filters** – edit `SENIOR_KEYWORDS`, `SMB_KEYWORDS`, or `ONTARIO_KEYWORDS` in `config.py`.
- **Change the newsletter look** – edit `templates/newsletter.html`.
- **Change the article cap** – update `MAX_ARTICLES` in `config.py` (default: 20).

