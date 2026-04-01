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
# Fourth-pass removals 2026-04-01:
#   IT World Canada                 – domain hijacked (casino spam)
#   IT Business Canada              – domain sold/parked
RSS_FEEDS = [
    # Canadian IT & small business – the Stonetown Digital Dispatch core audience
    {"name": "CanadianSME",        "url": "https://canadiansme.ca/feed/"},
    {"name": "Financial Post",     "url": "https://financialpost.com/feed/"},
    {"name": "BetaKit",            "url": "https://betakit.com/feed/"},
    {"name": "Small Business Trends", "url": "https://smallbiztrends.com/feed"},

    # Canadian seniors – a core segment of St. Marys small business owners
    {"name": "CARP",              "url": "https://www.carp.ca/feed/"},

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
    "retiree",
    "aging",
    "assistive technology",
    "health tech",
    "telehealth",
    "telemedicine",
    "OAS",
    "old age security",
    "CPP",
    "pension",
    "caregiver",
    "long-term care",
    "home care",
    "dementia",
    "cognitive decline",
    "aging in place",
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
    # Digital advocacy & IT-support terms – the Stonetown Digital Dispatch focus
    "digital literacy",
    "digital advocacy",
    "it support",
    "tech tip",
    "website",
    "social media",
    "email marketing",
    "digital marketing",
    "online presence",
    "search engine",
    "seo",
    "data privacy",
    "password",
    "backup",
    "broadband",
    "digital transformation",
    "local business",
    "main street",
]

ONTARIO_KEYWORDS = [
    "ontario",
    "toronto",
    "ottawa",
    "hamilton",
    "london",
    "mississauga",
    "brampton",
    "st. marys",
    "st marys",
    "perth county",
    "stratford",
    "southwestern ontario",
    "canada",
    "canadian",
]

# Keywords that signal a negative or fear-based article to be excluded.
NEGATIVE_KEYWORDS = [
    "scam",
    "fraud",
    "vulnerability",
    "risk",
    "danger",
    "warning",
    "threat",
    "exploit",
    "hack",
    "breach",
    "phishing",
    "malware",
    "decline",
    "loss",
    "crisis",
    "problem",
]

# Combined filter list used by the filter module
ALL_KEYWORDS = SENIOR_KEYWORDS + SMB_KEYWORDS + ONTARIO_KEYWORDS

# Maximum number of articles to include in a single newsletter
MAX_ARTICLES = 30

# Newsletter metadata
NEWSLETTER_TITLE = "The Stonetown Digital Dispatch | St. Marys Tech & IT Insights"
NEWSLETTER_SUBTITLE = "Get jargon-free tech tips, local IT support, and digital advocacy for St. Marys businesses from Ryan Wilson at Little Stone Tech Co. Subscribe for weekly insights."
