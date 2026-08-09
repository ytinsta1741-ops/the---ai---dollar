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
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
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

Rules:
- Output ONLY valid JSON, no markdown fences, no commentary.
- Exactly 7 slides.
- Every slide has: "text" (what appears on screen, 3-5 short lines separated by \\n, ALL CAPS words for emphasis are fine, max ~40 characters per line), "speech" (what the narrator says out loud for that slide, 1-3 natural spoken sentences, energetic tone), and "img" (a short, concrete, literal visual search phrase for a stock photo site — describe a real scene/person/object, e.g. "kid splitting a pizza into equal slices" or "person watering a small plant", NOT abstract ideas like "financial freedom" or "growth mindset").
- The "speech" and "img" for each slide MUST describe the same concrete scene — never mismatch them.
- The analogy must appear by slide 2 or 3, stated in one simple sentence a 10 year old would get instantly, BEFORE using the formal finance term.
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
