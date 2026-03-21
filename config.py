"""
Configuration for the newsletter scraper.

Defines RSS feed sources and keyword filters focused on tech news
relevant to seniors and small/medium businesses (SMBs) in Ontario, Canada.
"""

# RSS feed URLs – tech, business, and Canadian news sources
RSS_FEEDS = [
    # Canadian / Ontario business and tech
    {"name": "CBC Technology", "url": "https://www.cbc.ca/cmlink/rss-technology"},
    {"name": "CBC Business", "url": "https://www.cbc.ca/cmlink/rss-business"},
    {"name": "Globe and Mail Business", "url": "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/business/"},
    {"name": "Toronto Star Business", "url": "https://www.thestar.com/content/thestar/feed.RSSManagerServlet.articles.business.rss"},
    {"name": "Ontario Business Report", "url": "https://ontariobusiness.ca/feed/"},
    # Broad tech – curated for accessibility and SMB relevance
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
    {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
    {"name": "CNET", "url": "https://www.cnet.com/rss/news/"},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
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
MAX_ARTICLES = 20

# Newsletter metadata
NEWSLETTER_TITLE = "Ontario Tech Digest"
NEWSLETTER_SUBTITLE = "Weekly tech news for seniors and small businesses in Ontario, Canada"
