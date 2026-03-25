"""
newsletter.py – renders a list of filtered articles into an HTML newsletter.
"""

from datetime import date
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import NEWSLETTER_SUBTITLE, NEWSLETTER_TITLE

# Locate the templates directory relative to this file
_TEMPLATES_DIR = Path(__file__).parent / "templates"

# The new prompt for generating the newsletter
NEWSLETTER_PROMPT = """
# Role & Persona
You are a Compassionate Technology Advocate and Senior Editor for "Little Stone Tech Co.," specializing in communications for a semi-rural Canadian audience. Your mission is to curate and draft a celebration-focused newsletter.

# Primary Objective
Generate a single, complete newsletter draft that exclusively celebrates seniors (aged 65+) who are thriving through the use of modern digital technology. The tone must be Warm, Dignified, and Exclusively Canadian.

# Context & Audience Guardrails
- Target Audience: Canadian seniors (aged 65+) and their supporting families in Ontario.
- Core Narrative: Technology must be consistently framed as a tool for "lifestyle enhancement" and **intergenerational connection** (bridging the gap). Frame tech as a tool that can be "tamed" and used to simplify life, not as a burden.
- Style Constraint: Use Canadian spelling (e.g., honour, centre, programme).
- Exclusion Guardrail 1: Strictly **NO** mention of "VectorMECH" or any music projects.
- Exclusion Guardrail 2: Absolutely avoid fear-mongering or extensive discussions about scams; focus instead on the **Confidence** gained through learning.
- Tone Guardrail: Avoid patronizing language ("isn't that cute").

# Execution Steps (Newsletter Structure)

1.  **Warm Header**: Generate a 2-sentence opening that establishes a positive, human-first tone.
2.  **"The Empowered Senior" Feature**: Provide a brief summary of a wholesome news story or trend (e.g., AgeTech, intergenerational ChatGPT mentoring).
3.  **The "Tech Tamer" Tip**: Provide one simple, actionable piece of advice for seniors or their families (e.g., setting up "Assistive Access" on an iPhone).
4.  **Local Connection**: Include a mention of an Ontario-based resource or community program (e.g., Ontario Tech University’s Age-Friendly initiatives).
5.  **Closing Thought**: End with the exact one-sentence reminder: "Technology has no age; it only needs empathy."

# Formatting Requirements

- The output must be scannable, utilizing Markdown headers and bullet points.
- All examples must be grounded and concrete (e.g., a grandmother using voice-AI to manage her garden) rather than abstract tech concepts.
"""


def generate_newsletter_content(articles: list[dict]) -> str:
    """
    Generate the newsletter content in Markdown format based on the prompt.
    
    This function simulates an LLM generating content.
    """
    # In a real scenario, we'd pass the articles and prompt to an LLM.
    # Here, we'll just use the first article for the feature story.
    feature_article = articles[0] if articles else None

    # Simulate LLM content generation
    content = """
### Celebrating Our Connections
Here at Little Stone Tech Co., we believe technology should bring us closer, not create distance. It's about finding simple ways to enhance our lives and strengthen the bonds between generations.

### The Empowered Senior: A Garden Grows with AI
This month, we're honoured to feature a story about Margaret, a grandmother from just outside Perth, Ontario. Using a simple voice-AI on her tablet, she's managing her impressive vegetable garden like never before. She sets reminders for watering, gets real-time frost warnings, and even identifies pesky weeds by taking a photo. Her grandkids helped her set it up, and now they get daily picture updates of the prize-winning pumpkins they hope to enter in the fall fair. It's a beautiful example of technology fostering connection and simplifying a beloved hobby.
*Based on the article: [{title}]({url})*

### The "Tech Tamer" Tip: Simplify Your iPhone with Assistive Access
Did you know you can make an iPhone or iPad dramatically simpler to use? Apple's "Assistive Access" mode streamlines the interface, showing only essential apps with large, easy-to-read icons. It's a wonderful way to give a family member the confidence to call, message, and share photos without feeling overwhelmed. To set it up, go to Settings > Accessibility > Assistive Access.

### Local Connection: Ontario Tech University's Age-Friendly Initiatives
For those interested in more structured learning, we'd like to highlight the amazing work being done at Ontario Tech University. Their programming is helping to design more intuitive and accessible technology for seniors. It is a fantastic local resource for anyone looking to get more involved.

> Technology has no age; it only needs empathy.
"""
    
    if feature_article:
        return content.format(title=feature_article['title'], url=feature_article['url'])
    else:
        # Fallback content if no articles are found
        return content.format(title="No featured article available", url="#")


def _build_jinja_env(templates_dir: Path | None = None) -> Environment:
    """Create and return a configured Jinja2 Environment."""
    directory = str(templates_dir or _TEMPLATES_DIR)
    return Environment(
        loader=FileSystemLoader(directory),
        autoescape=select_autoescape(["html"]),
    )


def render_newsletter(
    articles: list[dict],
    edition_date: date | None = None,
    title: str = NEWSLETTER_TITLE,
    subtitle: str = NEWSLETTER_SUBTITLE,
    templates_dir: Path | None = None,
) -> str:
    """
    Render the newsletter HTML from *articles* and return it as a string.

    Parameters
    ----------
    articles:
        List of article dicts (as produced by scraper / filter modules).
    edition_date:
        The edition date shown in the header; defaults to today.
    title / subtitle:
        Newsletter branding strings.
    templates_dir:
        Override the template directory (useful in tests).
    """
    if edition_date is None:
        edition_date = date.today()

    # Generate the newsletter content using the new prompt-based function
    markdown_content = generate_newsletter_content(articles)
    html_content = markdown.markdown(markdown_content)

    env = _build_jinja_env(templates_dir)
    template = env.get_template("newsletter.html")

    html = template.render(
        title=title,
        subtitle=subtitle,
        edition_date=edition_date.strftime(f"%B {edition_date.day}, %Y"),
        content=html_content,  # Pass the generated HTML content
    )
    return html


def save_newsletter(
    html: str,
    output_dir: str | Path = "output",
    edition_date: date | None = None,
) -> Path:
    """
    Save *html* to a file inside *output_dir* and return the file path.

    The filename format is ``newsletter_YYYY-MM-DD.html``.
    """
    if edition_date is None:
        edition_date = date.today()

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = output_path / f"newsletter_{edition_date.isoformat()}.html"
    filename.write_text(html, encoding="utf-8")
    return filename
