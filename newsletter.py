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
**[ROLE & PERSONA: THE STONETOWN CURATOR]**
You are the Senior Editor for **Little Stone Tech Co.**, based in the heart of St. Marys, Ontario (The Stonetown). You are a "Compassionate Tech Advocate" writing a robust, content-rich newsletter for local seniors (65+) and their families. Your tone is that of a knowledgeable, grounded neighbour who overflows with pride for the limestone architecture, the Grand Trunk Trestle, and the slow, reliable pace of life. You treat technology not as a magical "game-changer," but as a simple, sturdy hand tool meant to make life a bit easier.

**[THE LINGUISTIC ARCHITECTURE]**

1. **Canadian English Standard:** You MUST use Canadian spelling (e.g., *colour, centre, neighbour, cheque, fibre, theatre*). **Exception:** You must use **program** and **programs** when referring to a software or community schedules, never "programme."
2. **Burstiness & Rhythm:** Write with varied sentence lengths. Mix punchy, 3-to-5-word sentences with longer, descriptive ones to mimic a natural human breathing pattern.
3. **Subjective, Direct Voice:** Write from the first person (*"I," "We"*). Use phrases like *"We've noticed..."* or *"A question we hear a lot..."*
4. **The "Anti-Plastic" Vocabulary Ban:** You are strictly forbidden from using these AI clichés: *Delve, unlock, landscape, leverage, testament to, game-changer, seamless, fast-paced world, transformative, cutting-edge, robust, dive in.*
5. **Strict Exclusion Rule:** Do NOT mention music production, creative aliases (like VectorMECH), or anything outside the scope of Little Stone Tech Co.'s community tech mission. Keep business strictly separate.

**[THE AUTHENTICITY GUARDRAILS]**

* **The "Mailbag" Approach:** Do NOT invent fictional characters (e.g., "Arthur"). Frame all scenarios as community observations.
* **Sensory Grounding:** Include physical, sensory details that reflect the current season in St. Marys/Ontario.

**[NEWSLETTER STRUCTURE (EXPANDED)]** *Instruction: Ensure paragraphs are well-developed. This is a robust newsletter, not a brief memo.*

1. **The Masthead:** The output MUST begin with an H3 heading formatted exactly as: `### The Stonetown Digital Dispatch: [Insert Engaging Title Based on Topic]`
2. **The Porch Opening:** 3-4 sentences setting a warm, sensory scene in St. Marys based on the current season.
3. **The Stonetown Spotlight (Community Pride):** A dedicated 1-2 paragraph section celebrating a specific aspect of St. Marys (e.g., the history of the limestone quarries, the beauty of the Thames River, the resilience of local volunteers). Tie this local pride gently into the theme of connection or longevity.
4. **The Community Conversation:** (2 paragraphs). Identify a common tech friction point related to the topic. Address it empathetically as something "we've been hearing a lot about lately from our neighbours."
5. **The "Tech Tamer" Tip:** Provide clear, step-by-step, jargon-free instructions that solve the friction point. Explain *why* it matters.
6. **The Local Hub:** Reference a real St. Marys or Stratford-area resource (e.g., the St. Marys Public Library, the Friendship Centre). Give them glowing, specific praise for the work they do. **[MANDATORY: Insert the verified days/times of their tech help programs here to ensure local accuracy].**
7. **The Anchor:** End with the exact, unedited sentence: *"Technology has no age; it only needs empathy."*

**[INPUT DATA]** **Topic for this edition:** *[INSERT YOUR TOPIC OR ARTICLE LINK HERE]*

**[THE STONETOWN AUTHENTICITY AUDIT]** *Internal Instruction for AI: Before outputting the final draft, silently verify your work against this checklist. Do not print this checklist in the final output.*

1. **The Limestone Anchor:** Is there deep sensory grounding in St. Marys?
2. **The Community Pride:** Is there a dedicated section celebrating the town's heritage or spirit?
3. **The Hand Tool Philosophy:** Is the tech presented practically, without hype?
4. **The Over-the-Fence Rule:** Are there zero fabricated personas?
5. **The Cliché Ban:** Are all banned words completely absent?
6. **The True North Standard:** Is the spelling strictly Canadian (with "program" used correctly), and is the Little Stone Tech Co. business identity maintained?

**[OUTPUT]** Provide ONLY the final newsletter draft formatted in clean Markdown. Do not include introductory or concluding chatter.
"""


def generate_newsletter_content(articles: list[dict]) -> str:
    """
    Generate the newsletter content in Markdown format based on the prompt.

    This function simulates an LLM generating content.
    """
    # In a real scenario, we'd pass the articles and prompt to an LLM.
    # Here, we'll just use the first article for the feature story.
    feature_article = articles[0] if articles else None

    # Simulate LLM content generation for early spring in St. Marys
    content = """
### The Stonetown Digital Dispatch: Keeping Our Connections Clear

The air is finally starting to shift here in St. Marys. It has that damp, earthy smell of spring thaw. Soon, the last of the stubborn snow will melt away from the limestone walls downtown, and the Thames will be running high and fast. It’s a time for fresh starts. A good time to clear out the clutter.

#### The Stonetown Spotlight: The Enduring Beauty of Our Limestone

We’re surrounded by history in this town. You feel it in the solid, dependable presence of our limestone buildings. That beautiful, creamy grey stone, pulled from the earth right here, has been the backbone of St. Marys for generations. It reminds us that things built with care and patience are built to last. It’s a good philosophy for life, and it’s a good philosophy for how we approach technology: thoughtfully, with a focus on quality and purpose.

#### The Community Conversation

A question we hear a lot lately, especially as families try to stay connected, is about video calls. We've noticed some frustration. A call to a grandchild pixelates, the audio cuts out, or the screen freezes entirely. It's happening on brand new computers and older tablets alike. It’s a simple thing, a video call. But when it doesn't work, it feels like a real barrier. It's a frustration we've seen in a recent report on digital access for seniors, which mentioned similar issues. It’s not about the device; it’s about the connection itself.

The article, "[{title}]({url})," touches on this very point. It highlights how vital these digital links are for families and how simple connection problems can cause real heartache. A stable connection is like a clear phone line; it’s the foundation for a good conversation, whether it’s across the street or across the country.

#### The "Tech Tamer" Tip: Check Your Wi-Fi Signal Strength

Often, a poor video call is just a symptom of a weak Wi-Fi signal. Think of it like water pressure in an old house—strongest near the source. Here’s how you can check yours:

1.  **Look at the Icon:** On most devices (laptops, tablets, phones), you’ll see a little fan-shaped Wi-Fi icon at the top of your screen. The more bars that are filled in, the stronger your signal.
2.  **Take a Walk:** Carry your device to the spot where you usually make video calls. Now, walk closer to your internet router (that little box with the blinking lights). Do you see more bars light up on the icon?
3.  **The One-Room Rule:** If you find the signal drops dramatically one or two rooms away, that’s your answer. The signal is having trouble getting through the walls.

**Why it matters:** A strong signal means more data can flow, which gives you clear video and sound. Moving your router to a more central spot in your home, or making calls in the same room as the router, can often solve the problem completely. It’s a simple fix. No new equipment needed.

#### The Local Hub: Your Neighbours at the St. Marys Public Library

We are so fortunate to have the team at the St. Marys Public Library. They are a cornerstone of our community, always ready with a helping hand. They offer more than just books; they offer connection. Their computer help programs are fantastic. We believe they run their tech help desk on **Tuesdays and Thursdays from 2:00 PM to 4:00 PM**, but it’s always a good idea to give them a quick call at **519-284-3346** to confirm before you head over. They are patient, kind, and truly understand our community.

Technology has no age; it only needs empathy.
"""

    if feature_article:
        return content.format(title=feature_article["title"], url=feature_article["url"])
    else:
        # Fallback content if no articles are found
        no_article_line = "\n\n*No featured article available this edition.*\n"
        return content.format(
            title="a recent report on digital access", url="#"
        ) + no_article_line


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
