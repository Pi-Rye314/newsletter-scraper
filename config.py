"""
Configuration for the newsletter scraper.

Defines RSS feed sources and keyword filters focused on tech news
relevant to seniors and small/medium businesses (SMBs) in Ontario, Canada.
"""

# RSS feed URLs – senior-focused, Canadian, and broad tech sources.
# Dead/blocked feeds removed 2026-03-21:
#   CBC Technology / CBC Business  – consistent read timeouts
#   Toronto Star Business           – malformed feed response
#   Ontario Business Report         – HTTP 404 (domain gone)
#   Wired                           – HTTP 403 (blocks scrapers)
# Second-pass removals 2026-03-21:
#   CBC Health                      – read timeout
#   Ontario Government News         – malformed XML
#   AARP News                       – HTTP 404 (URL changed)
#   NIA                             – HTTP 405 (no GET on feed endpoint)
# Third-pass removals 2026-03-21:
#   ScienceDaily Aging              – HTTP 404 (feed path removed)
#   NCOA                            – HTTP 404 (no RSS endpoint)
#   McKnight's Senior Living        – HTTP 302 redirect loop
RSS_FEEDS = [
    # Canadian seniors & health – primary audience feeds
    {"name": "CARP",              "url": "https://www.carp.ca/feed/"},
    {"name": "Healthy Debate",    "url": "https://healthydebate.ca/feed/"},
    {"name": "Retire Happy",       "url": "https://www.retirehappy.ca/feed/"},

    # North American seniors – high-volume, keyword-rich content
    {"name": "LeadingAge",         "url": "https://leadingage.org/feed/"},
    {"name": "AgingInPlace.com",   "url": "https://www.aginginplace.com/feed/"},

    # Working tech / business feeds kept from original list
    {"name": "Globe and Mail Business", "url": "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/business/"},
    {"name": "TechCrunch",        "url": "https://techcrunch.com/feed/"},
    {"name": "CNET",              "url": "https://www.cnet.com/rss/news/"},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Ars Technica",      "url": "https://feeds.arstechnica.com/arstechnica/index"},
]

# Keywords that make an article relevant to the target audience.
# Articles matching any keyword (case-insensitive) in title or summary are kept.
SENIOR_KEYWORDS = [
    "senior",
    "seniors",
    "elder",
    "elderly",
    "retirement",
    "retire",
    "aging",
    "accessibility",
    "assistive technology",
    "digital literacy",
    "health tech",
    "telehealth",
    "telemedicine",
    "medicare",
    "pension",
    "caregiver",
    "long-term care",
    "home care",
]

SMB_KEYWORDS = [
    "small business",
    "smb",
    "sme",
    "entrepreneur",
    "startup",
    "freelance",
    "self-employed",
    "sole proprietor",
    "e-commerce",
    "ecommerce",
    "productivity",
    "cybersecurity",
    "cloud",
    "ai tool",
    "artificial intelligence",
    "automation",
    "accounting software",
    "payroll",
    "invoice",
    "grant",
    "funding",
    "loan",
]

ONTARIO_KEYWORDS = [
    "ontario",
    "toronto",
    "ottawa",
    "hamilton",
    "london",
    "mississauga",
    "brampton",
    "canada",
    "canadian",
]

# Combined filter list used by the filter module
ALL_KEYWORDS = SENIOR_KEYWORDS + SMB_KEYWORDS + ONTARIO_KEYWORDS

# Maximum number of articles to include in a single newsletter
MAX_ARTICLES = 30

# Newsletter metadata
NEWSLETTER_TITLE = "Ontario Tech Digest"
NEWSLETTER_SUBTITLE = "Weekly tech news for seniors and small businesses in Ontario, Canada"
