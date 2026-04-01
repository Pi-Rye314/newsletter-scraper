"""Newsletter module: generate, quality-gate, and render newsletters to HTML.

Provides content generation from articles, deterministic quality gate enforcement
(regional reach, cyber actions, topic alignment), and HTML rendering via Jinja2 templates.
"""

import logging
from datetime import date
from pathlib import Path
import re

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

from config import NEWSLETTER_SUBTITLE, NEWSLETTER_TITLE

# Locate the templates directory relative to this file
_TEMPLATES_DIR = Path(__file__).parent / "templates"
_FEATURE_CANDIDATE_LIMIT = 3

_TOPIC_MARKERS = {
    "payroll": {"payroll", "invoice", "bookkeep", "accounting", "tax", "cash flow", "remittance"},
    "video": {"video", "zoom", "wifi", "wi-fi", "call"},
    "cyber": {"security", "cyber", "phishing", "password", "2fa", "two-factor", "fraud"},
    "business": {"small business", "smb", "retail", "shop", "owner", "sales"},
    "digital_confidence": {
        "digital confidence",
        "digital skills",
        "digital literacy",
        "online safety",
        "device basics",
        "tech support",
        "jargon-free",
    },
    "digital_inclusion": {
        "digital divide",
        "bridge the divide",
        "inclusion",
        "accessible",
        "accessibility",
        "equity",
        "connected community",
    },
    "digital_advocacy": {
        "digital advocacy",
        "community support",
        "neighbour",
        "local help",
        "community hub",
        "confidence-building",
    },
}

_NOISY_TITLE_MARKERS = {
    "appointed",
    "ceo",
    "board",
    "dividend",
    "earnings",
    "quarter",
    "conference call",
}

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
6. **The Local Hub:** Make this section community-wide. Speak to business owners, seniors, families, students, and newcomers together. Offer practical confidence-building actions people can take this week, and point readers to local groups where neighbours help neighbours with technology.
7. **The Anchor:** End with the exact, unedited sentence: *"The true measure of our progress isn't found in the speed of our processors, but in the reach of our inclusion. As we bridge the digital divide right here at home, we prove that innovation is most powerful when it serves the heart of the community. Technology has no age; it only needs empathy."*

**[INPUT DATA]** **Topic for this edition:** {topic_for_edition}

**[THE STONETOWN AUTHENTICITY AUDIT]** *Internal Instruction for AI: Before outputting the final draft, silently verify your work against this checklist. Do not print this checklist in the final output.*

1. **The Limestone Anchor:** Is there deep sensory grounding in St. Marys?
2. **The Community Pride:** Is there a dedicated section celebrating the town's heritage or spirit?
3. **The Hand Tool Philosophy:** Is the tech presented practically, without hype?
4. **The Over-the-Fence Rule:** Are there zero fabricated personas?
5. **The Cliché Ban:** Are all banned words completely absent?
6. **The True North Standard:** Is the spelling strictly Canadian (with "program" used correctly), and is the Little Stone Tech Co. business identity maintained?

**[OUTPUT]** Provide ONLY the final newsletter draft formatted in clean Markdown. Do not include introductory or concluding chatter.
"""


def _article_option_score(article: dict) -> int:
    """Score an article for feature suitability based on topic richness."""
    title = str(article.get("title", ""))
    summary = str(article.get("summary", ""))
    combined = f"{title} {summary}".lower()

    practical_groups = (
        "payroll",
        "video",
        "cyber",
        "digital_confidence",
        "digital_inclusion",
        "digital_advocacy",
    )

    group_hits = 0
    marker_hits = 0
    practical_group_hits = 0
    for group_name, markers in _TOPIC_MARKERS.items():
        group_matched = False
        for marker in markers:
            if marker in combined:
                marker_hits += 1
                group_matched = True
        if group_matched:
            group_hits += 1
            if group_name in practical_groups:
                practical_group_hits += 1

    # Favor headlines with clearer human-readable framing.
    readability_bonus = min(len(title.split()), 12)
    noisy_penalty = sum(1 for marker in _NOISY_TITLE_MARKERS if marker in title.lower()) * 12

    # Strongly favor practical topics over generic corporate news.
    return (practical_group_hits * 20) + (group_hits * 6) + (marker_hits * 2) + readability_bonus - noisy_penalty


def _select_feature_article(articles: list[dict], top_n: int = _FEATURE_CANDIDATE_LIMIT) -> dict:
    """Choose the best feature article from top candidates for variety and relevance."""
    if not articles:
        return {}

    candidates = articles[:top_n]
    best_index = 0
    best_score = _article_option_score(candidates[0])

    for idx, candidate in enumerate(candidates[1:], start=1):
        score = _article_option_score(candidate)
        if score > best_score:
            best_score = score
            best_index = idx

    # If all top candidates score poorly, keep recency and use the first article.
    if best_score < 12:
        best_index = 0
        best_score = _article_option_score(candidates[0])

    selected = candidates[best_index]
    logger.info(
        "FEATURE_PICK: selected #%d/%d with score=%d title='%s'",
        best_index + 1,
        len(candidates),
        best_score,
        selected.get("title", "Untitled article"),
    )
    return selected


def _topic_for_edition(feature_article: dict) -> str:
    """Build a topic line from selected feature article."""
    if not feature_article:
        return "No scraped article available"

    title = feature_article.get("title", "Untitled article")
    url = feature_article.get("url", "#")
    return f"[{title}]({url})"


def _topic_sections(feature_title: str, feature_reference: str) -> tuple[str, str]:
    """Return topic-aligned Community Conversation and Tech Tamer sections."""
    lowered = feature_title.lower()

    payroll_markers = {
        "payroll",
        "invoice",
        "bookkeep",
        "accounting",
        "tax",
        "cash flow",
        "remittance",
    }
    video_markers = {"video", "zoom", "wifi", "wi-fi", "call"}

    if any(marker in lowered for marker in payroll_markers):
        community = f"""
#### The Community Conversation

A question we hear a lot lately from business owners and family-run shops is about payroll confidence. People worry they will miss a deduction, submit numbers late, or lose track of who was paid and when. That stress usually builds up when records live in too many places at once.

The article, \"{feature_reference},\" points to practical payroll features that can reduce that pressure. The goal is not to add complexity. It is to make payday predictable, reduce last-minute scrambling, and keep a clear record trail that helps during tax season.
"""

        tip = """
#### The "Tech Tamer" Tip: Build a 10-Minute Payroll Check

Before each pay run, do this short check:

1.  **Confirm Hours and Rates:** Match submitted hours with current wage rates in one sheet.
2.  **Review Deductions:** Verify CPP, EI, and tax fields before finalizing payroll.
3.  **Save a Snapshot:** Export the payroll summary and store it in a dated folder for easy reference.

**Why it matters:** A quick routine like this catches small mistakes early, helps you answer staff questions faster, and keeps your records ready for month-end and tax reporting.
"""
        return community, tip

    if any(marker in lowered for marker in video_markers):
        community = f"""
#### The Community Conversation

A question we hear a lot lately, especially as families try to stay connected, is about video calls. We've noticed some frustration. A call to a grandchild pixelates, the audio cuts out, or the screen freezes entirely. It's happening on brand new computers and older tablets alike. It is a simple thing, a video call. But when it does not work, it feels like a real barrier.

The article, \"{feature_reference},\" touches on this very point. It highlights how vital these digital links are for families and how simple connection problems can cause real heartache. A stable connection is like a clear phone line; it is the foundation for a good conversation, whether it is across the street or across the country.
"""

        tip = """
#### The "Tech Tamer" Tip: Check Your Wi-Fi Signal Strength

Often, a poor video call is just a symptom of a weak Wi-Fi signal. Think of it like water pressure in an old house, strongest near the source. Here is how you can check yours:

1.  **Look at the Icon:** On most devices (laptops, tablets, phones), you will see a fan-shaped Wi-Fi icon at the top of your screen. The more bars that are filled in, the stronger your signal.
2.  **Take a Walk:** Carry your device to the spot where you usually make video calls. Now walk closer to your internet router (the box with blinking lights). Do you see more bars light up?
3.  **Use the One-Room Rule:** If the signal drops sharply one or two rooms away, the walls are weakening your connection.

**Why it matters:** A strong signal means smoother video and clearer sound. Moving your router to a more central spot can often solve the problem without buying new equipment.
"""
        return community, tip

    community = f"""
#### The Community Conversation

A question we hear often is how to keep digital work simple when there are too many apps, logins, and alerts. People are not looking for more tools. They want fewer surprises and a routine they can trust.

The article, \"{feature_reference},\" reflects that same need for practical systems. When the basics are clear and repeatable, technology starts feeling useful instead of noisy.
"""

    tip = """
#### The "Tech Tamer" Tip: Create a Weekly Digital Reset

Set aside ten minutes each week for this reset:

1.  **Update Devices:** Install pending updates on your phone and computer.
2.  **Review Accounts:** Check recovery email, two-factor settings, and recent sign-ins.
3.  **Tidy Your Files:** Move key documents into clearly named folders so they are easy to find.

**Why it matters:** A simple weekly reset prevents avoidable problems and gives you more confidence using your tools every day.
"""
    return community, tip


def _apply_quality_gates(newsletter: str, feature_title: str) -> str:
    """Enforce baseline quality checks and auto-correct when needed."""
    lowered = newsletter.lower()
    gates_triggered = []

    # Gate 1: Regional reach (must include St. Marys and either Stratford or Perth County).
    has_st_marys = "st. marys" in lowered or "st marys" in lowered
    has_surrounding = "stratford" in lowered or "perth county" in lowered
    if has_st_marys and not has_surrounding:
        newsletter += (
            "\n\nFor neighbours in Stratford and across Perth County, these same habits "
            "apply just as well at home, at work, and in local community spaces."
        )
        gates_triggered.append("regional_reach (TRIGGERED)")
        lowered = newsletter.lower()
    else:
        gates_triggered.append("regional_reach (passed)")

    # Gate 2: Cyber-action minimum (at least three concrete actions).
    action_markers = [
        "two-factor",
        "2fa",
        "password",
        "phishing",
        "suspicious",
        "update",
        "backup",
    ]
    action_hits = sum(1 for marker in action_markers if marker in lowered)
    if action_hits < 3:
        newsletter += (
            "\n\nBefore the week ends, do these three things: turn on two-factor "
            "authentication, update your devices, and change one reused password."
        )
        gates_triggered.append(f"cyber_actions (TRIGGERED - had {action_hits}, need 3)")
    else:
        gates_triggered.append(f"cyber_actions (passed - {action_hits} markers found)")

    # Gate 3: Topic/body alignment. Ensure at least one meaningful topic token appears.
    topic_tokens = [
        token
        for token in re.findall(r"[a-zA-Z]{4,}", feature_title.lower())
        if token not in {"with", "from", "that", "this", "your", "into", "about", "features"}
    ]
    if topic_tokens and not any(token in newsletter.lower() for token in topic_tokens[:4]):
        newsletter += (
            f"\n\nThis edition's feature, \"{feature_title}\", reinforces the same "
            "goal: practical digital confidence for everyday life and local business."
        )
        gates_triggered.append("topic_alignment (TRIGGERED)")
    else:
        gates_triggered.append("topic_alignment (passed)")

    # Log all gates
    logger.info(f"QUALITY_GATES: {' | '.join(gates_triggered)}")
    
    return newsletter


def generate_newsletter_content(articles: list[dict]) -> str:
    """
    Generate the newsletter content in Markdown format based on the prompt.

    This function simulates an LLM generating content.
    """
    # In a real scenario, we'd pass the articles and prompt to an LLM.
    # We keep the prompt topic in sync with the selected feature article.
    feature_article = _select_feature_article(articles)
    topic_for_edition = _topic_for_edition(feature_article)
    _resolved_prompt = NEWSLETTER_PROMPT.format(topic_for_edition=topic_for_edition)

    feature_title = feature_article.get("title", "a recent report on digital access")
    feature_url = feature_article.get("url", "#")
    feature_reference = f"[{feature_title}]({feature_url})"
    community_section, tip_section = _topic_sections(feature_title, feature_reference)

    # Simulate LLM content generation for early spring in St. Marys
    content = """
### The Stonetown Digital Dispatch: Keeping Our Connections Clear

**Topic for this edition:** {topic_for_edition}

The air is finally starting to shift here in St. Marys. It has that damp, earthy smell of spring thaw. Soon, the last of the stubborn snow will melt away from the limestone walls downtown, and the Thames will be running high and fast. It’s a time for fresh starts. A good time to clear out the clutter.

#### The Stonetown Spotlight: The Enduring Beauty of Our Limestone

We’re surrounded by history in this town. You feel it in the solid, dependable presence of our limestone buildings. That beautiful, creamy grey stone, pulled from the earth right here, has been the backbone of St. Marys for generations. It reminds us that things built with care and patience are built to last. It’s a good philosophy for life, and it’s a good philosophy for how we approach technology: thoughtfully, with a focus on quality and purpose.

{community_section}

{tip_section}

#### Cyber Confidence on Main Street: Your Local Hub

Cybersecurity works best when it feels like a shared community habit, not a private burden. On Main Street and on side streets, the same three steps protect nearly everyone: turn on two-factor authentication, update devices every week, and pause before clicking urgent links. These are small actions, but they create real confidence for shop owners, retirees, parents, students, and anyone working online.

This week, invite one person in your circle to do a 15-minute "cyber check-in" with you. Review passwords, confirm account recovery emails, and practice spotting a suspicious message together. Community confidence grows one conversation at a time, and every neighbour who feels safer online makes our whole town stronger.


Technology has no age; it only needs empathy.
"""

    newsletter = content.format(
        topic_for_edition=topic_for_edition,
        community_section=community_section,
        tip_section=tip_section,
    )

    newsletter = _apply_quality_gates(newsletter, feature_title)
    if articles:
        return newsletter

    # Fallback content if no articles are found
    no_article_line = "\n\n*No featured article available this edition.*\n"
    return newsletter + no_article_line


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
    logger.debug(f"Output directory ensured: {output_path.absolute()}")

    filename = output_path / f"newsletter_{edition_date.isoformat()}.html"
    filename.write_text(html, encoding="utf-8")
    
    file_size_kb = filename.stat().st_size / 1024
    logger.debug(f"Newsletter file written: {filename.name} ({file_size_kb:.1f} KB)")
    
    return filename
