"""AI-generated video scripts using Google Gemini (free tier).

Falls back to the template system in topic_generator.py if the API
key is missing, the request fails, or the response is malformed —
so the channel never stops posting because of an AI outage.
"""
import os
import re
import json
import random
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

FINANCE_TERMS = [
    # Personal finance
    "compound interest", "index fund", "dividend", "inflation", "credit score",
    "diversification", "asset allocation", "liquidity", "bull market", "bear market",
    "market capitalization", "P/E ratio", "expense ratio", "bond yield", "amortization",
    "equity", "REIT", "capital gains", "tax bracket", "emergency fund",
    "net worth", "cash flow", "APR vs APY", "credit utilization", "recession",
    "mutual fund", "ETF", "principal", "collateral", "appreciation vs depreciation",
    "opportunity cost", "arbitrage", "leverage", "portfolio rebalancing", "vesting",
    "401k match", "Roth vs Traditional", "escrow", "underwriting", "FICO score",
    # Accounting / corporate finance
    "income statement", "balance sheet (statement of financial position)",
    "cash flow statement", "debenture", "assets vs liabilities", "shareholders equity",
    "retained earnings", "accounts receivable", "accounts payable", "working capital",
    "gross margin", "net margin", "EBITDA", "depreciation", "accrual accounting",
    "revenue recognition", "goodwill", "current ratio", "debt-to-equity ratio",
    "operating expenses vs capital expenses", "bonds vs stocks", "par value",
    "book value vs market value", "fiscal year", "audit", "general ledger",
]

SYSTEM_PROMPT = """You write scripts for "The AI Dollar", a YouTube Shorts channel where every video explains ONE real finance or accounting term to a complete beginner — the way you'd explain it to a smart 10 year old, using a simple real-world analogy, not a lecture. Terms range from everyday personal finance (credit score, compound interest) to accounting/corporate finance (income statement, balance sheet, debenture, cash flow statement) — treat both equally seriously and explain any abbreviation in full the first time (e.g. "SOFP — that stands for Statement Of Financial Position, what most people just call a balance sheet").

Do NOT make generic "money rules", "money tips", or "habits of the rich" listicle videos. Every video must center on ONE specific finance term or concept (you'll be given one, or pick one from the same category if none is given) and unpack it fully:
1. What everyday situation does this remind you of? (the analogy — a game, a garden, a jar of candy, splitting a pizza, a video game power-up, anything a 10 year old already understands)
2. What does the term actually mean in finance, in one plain sentence?
3. A concrete real-number example showing it in action.
4. Why it actually matters to the viewer's own money.

FRAME IT AS A TENSION OR COMPARISON, not a flat definition. Real audience data on this channel shows comparison-framed videos ("Stocks vs Bonds") get 3x the retention of plain "What is X" definition videos. So:
- If the term naturally has a counterpart (Bull vs Bear, APR vs APY, Assets vs Liabilities, Roth vs Traditional, Stocks vs Bonds), frame the whole video as that head-to-head comparison — title, hook, and structure should all lean into the "vs".
- If the term doesn't have an obvious counterpart, frame it as friend-vs-enemy tension instead (e.g. "Compound Interest: is it working FOR you or AGAINST you?", "Is your amortization schedule secretly costing you thousands?") — never just "What is [term]".
- The title must promise a winner, a surprise, or a choice — not just a definition.

VOICE: Talk like you're excitedly explaining this to a friend who just asked "wait what does that even mean" — not like you're reading a dictionary entry. Concretely:
- Short sentences. Never more than ~12 words per sentence. Break long ideas into two punchy sentences instead of one dense one.
- Use "you" constantly — make it about the viewer's own money, not abstract theory.
- Contractions always (it's, you're, don't) — never formal/stiff phrasing.
- Vary sentence length and rhythm — a punchy 3-word sentence, then a slightly longer one. Reading it out loud should sound like a person talking, not a textbook.
- Every slide should feel like it's building toward something, not just delivering a flat fact. End slides on a hook into the next one where possible ("But here's the part nobody tells you...").
- Zero filler, zero throat-clearing ("So basically...", "Let's dive in..."). Start every sentence already saying something.

Rules:
- Output ONLY valid JSON, no markdown fences, no commentary.
- Exactly 7 slides.
- Every slide has "text", "speech", and "img":
  - "speech" is what the narrator says out loud, 1-3 short punchy spoken sentences (see VOICE above), energetic and conversational, never lecture-toned.
  - "text" is the on-screen caption — it MUST be a short, verbatim excerpt taken directly from that same slide's "speech" (the single most important phrase or sentence, trimmed to fit, 3-5 short lines separated by \\n, max ~40 characters per line, ALL CAPS words for emphasis are fine). NEVER write different wording on screen than what is spoken — no separate paraphrase, no new phrasing that doesn't appear in "speech".
  - "img" is a short, concrete visual search phrase for a stock photo site. It must ALWAYS depict a real finance/business/office scene (e.g. stock charts, cash, calculators, laptops with spreadsheets, bank buildings, people reviewing documents, coins, piggy banks) — NEVER depict the analogy literally (no kids, pizza, gardens, games, toys, animals). The image should relate to what's being discussed, expressed through finance/business imagery, not abstract ideas like "financial freedom".
- The analogy must appear by slide 2 or 3, stated in one simple sentence a 10 year old would get instantly, BEFORE using the formal finance term. The analogy lives in the spoken words and captions — never in the imagery.
- Slide 1 is the hook — name the term and promise it'll finally make sense, or open with the analogy itself as a curiosity hook.
- Slide 7 is the ending — recap the term and the analogy together in one sentence, then tell the viewer to follow for the next term (do not literally write "SUBSCRIBE" as the whole slide, the app already adds a subscribe button automatically).
- Use specific, believable numbers (dollar amounts, percentages, timeframes) in the real-number example — never vague claims.
- Never mention any brand, bank, or app name that could be factually wrong or outdated; prefer generic terms like "a high-yield savings account".
- Output JSON shape exactly:
{"title": "...", "keywords": ["...", "...", "..."], "slides": [{"text": "...", "speech": "...", "img": "..."}, ... exactly 7 objects]}
"""


def _extract_json(raw_text):
    raw_text = raw_text.strip()
    raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text)
    raw_text = re.sub(r'\s*```$', '', raw_text)
    return json.loads(raw_text)


def _validate_topic(data):
    if not isinstance(data, dict):
        return False
    if not data.get("title") or not isinstance(data.get("slides"), list):
        return False
    if len(data["slides"]) != 7:
        return False
    for slide in data["slides"]:
        if not all(k in slide and slide[k] for k in ("text", "speech", "img")):
            return False
    if not data.get("keywords"):
        data["keywords"] = [data["title"].split()[0], "Personal Finance", "Money Tips"]
    return True


def generate_ai_topic(existing_titles_hint=""):
    """Ask Gemini for one complete 7-slide short-form topic. Returns None on any failure."""
    if not GEMINI_API_KEY:
        print("[WARN] GEMINI_API_KEY not set, skipping AI generation")
        return None

    term = random.choice(FINANCE_TERMS)
    user_prompt = f"Write a new video explaining the finance term: \"{term}\"."
    if existing_titles_hint:
        user_prompt += f" Make it clearly different from these already-posted titles: {existing_titles_hint}."

    payload = {
        "contents": [{"parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "generationConfig": {
            "temperature": 1.1,
            "maxOutputTokens": 3000,
            "responseMimeType": "application/json",
        },
    }

    try:
        resp = requests.post(
            GEMINI_URL,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=30,
        )
        if resp.status_code != 200:
            print(f"[WARN] Gemini API error {resp.status_code}: {resp.text[:200]}")
            return None

        data = resp.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        topic = _extract_json(raw_text)

        if not _validate_topic(topic):
            print("[WARN] Gemini returned malformed topic, falling back to templates")
            return None

        return topic

    except Exception as e:
        print(f"[WARN] Gemini generation failed: {e}")
        return None
