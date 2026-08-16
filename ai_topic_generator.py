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

# Google keeps retiring/restricting Gemini models to billing-only tiers
# (2.0-flash retired, 2.5-flash "no longer available to new users",
# 3.6-flash requires billing on this key). Rather than hardcode one model
# and keep breaking, try several known free-tier-eligible models in order.
GEMINI_MODEL_CANDIDATES = [
    os.getenv("GEMINI_MODEL"),  # optional manual override, tried first if set
    "gemini-3.5-flash-lite",
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite",
    "gemini-flash-lite-latest",
]
GEMINI_MODEL_CANDIDATES = [m for m in GEMINI_MODEL_CANDIDATES if m]


def _gemini_url(model):
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

CONFUSABLE_PAIRS = [
    ("loan", "debenture"), ("overdraft", "loan"),
    ("revenue", "profit"), ("gross profit", "net profit"),
    ("cash flow", "profit"), ("interest rate", "APR"), ("stocks", "shares"),
    ("bonds", "stocks"), ("credit", "debit"), ("savings account", "fixed deposit"),
    ("tax deduction", "tax credit"), ("insurance", "assurance"), ("mortgage", "personal loan"),
    ("depreciation", "amortization"), ("markup", "margin"), ("invoice", "receipt"),
    ("fixed cost", "variable cost"),
    ("capital expenditure", "operating expenditure"), ("bull market", "bear market"),
    ("Roth IRA", "Traditional IRA"), ("APR", "APY"), ("debit card", "credit card"),
    ("line of credit", "loan"), ("recession", "depression"), ("inflation", "deflation"),
    ("simple interest", "compound interest"), ("wholesale price", "retail price"),
    ("net worth", "net income"), ("dividend", "capital gains"),
    ("secured loan", "unsecured loan"), ("term insurance", "whole life insurance"),
    ("nominal value", "market value"), ("working capital", "fixed capital"),
    ("trial balance", "balance sheet"), ("debenture", "share"),
]

SYSTEM_PROMPT = """You are an expert financial educator and content creator writing scripts for "The AI Dollar", a YouTube Shorts channel. Every video takes TWO real finance or accounting terms that people genuinely confuse with each other (you'll be given the pair, e.g. "loan" vs "debenture") and clearly differentiates them for a complete beginner — the way you'd explain it to a smart 10 year old, using simple real-world analogies, not a lecture. Explain any abbreviation in full the first time it appears.

STRUCTURE — every video follows this arc across the 7 slides:
1. Hook: name both confusable terms and promise the viewer will never mix them up again.
2. Term A explained with its own simple analogy (a comparison to something everyday — an activity, a relationship, a situation, not necessarily a literal object).
3. Term B explained with ITS OWN separate, different analogy — term B must NOT reuse term A's analogy, they need to feel like two distinct things.
4. The direct differentiation: state in one crisp sentence exactly what separates them.
5. A concrete real-number example showing both terms side by side in action (real dollar amounts).
6. Why getting this confused actually costs the viewer money or causes real problems.
7. Recap both terms and their key difference in one sentence, then tell the viewer to follow for the next confusable pair.

IMAGES MUST DIFFERENTIATE THE TWO TERMS. Slides about Term A need a DIFFERENT image concept than slides about Term B — e.g. if comparing "loan" vs "debenture", a loan slide might show a bank loan officer or a person signing paperwork at a bank, while a debenture slide shows a bond certificate or investment document — visually distinct so the viewer's eye associates a different picture with each term. Never reuse the same visual concept for both terms.

When a slide's example or analogy naturally involves a well-known finance/business figure (e.g. explaining equity/investing with Warren Buffett, the Federal Reserve with Jerome Powell, entrepreneurship with Elon Musk or Jeff Bezos), you may set "img" to just that person's exact full name instead of a scene description — the app will fetch an appropriately licensed photo. Only use figures from this safe list: Warren Buffett, Jerome Powell, Elon Musk, Jeff Bezos, Bill Gates, Mark Cuban, Janet Yellen, Ray Dalio, Charlie Munger. Do not invent other names.

FRAME THE TITLE around the confusion itself, not a flat definition. Real audience data on this channel confirms two hook styles clearly outperform plain "What is X" videos:
- CONFUSION-CALLOUT: "You've Been Mixing Up [A] and [B] — Here's The Difference", "[A] vs [B]: The Difference Nobody Explains"
- PERSONAL-STAKES QUESTION: "Do You Actually Know The Difference Between [A] and [B]?", "Is Confusing These Two Costing You Money?" — this style has been the single best-performing hook on this channel so far.
- The title must always promise clarity on a real confusion — never a plain definition.

VOICE: Explain it like you're talking to a smart 10 year old who's never heard either word before — not like you're reading a dictionary entry. Be VERY compact. Concretely:
- Max 2 short sentences per slide. Never more than ~10 words per sentence. If an idea needs more than that, cut it down or move it to the next slide — do not cram.
- One idea per slide, always. The differentiation slide (4) states the ONE core difference in a single sentence — not a list of several differences, just the one thing that matters most.
- Use "you" constantly — make it about the viewer's own money, not abstract theory.
- Contractions always (it's, you're, don't) — never formal/stiff phrasing.
- Speak SLOWLY and simply — short words over long ones, simple structure over clever structure.
- Zero filler, zero throat-clearing ("So basically...", "Let's dive in..."). Start every sentence already saying something.
- If you'd have to explain a word you just used, you used the wrong word — replace it with a simpler one.

Rules:
- Output ONLY valid JSON, no markdown fences, no commentary.
- Exactly 7 slides.
- Every slide has "text", "speech", and "img":
  - "speech" is what the narrator says out loud, 1-3 short punchy spoken sentences (see VOICE above), energetic and conversational, never lecture-toned.
  - "text" is the on-screen caption — it MUST be a short, verbatim excerpt taken directly from that same slide's "speech" (the single most important phrase or sentence, trimmed to fit, 3-5 short lines separated by \\n, max ~40 characters per line, ALL CAPS words for emphasis are fine). NEVER write different wording on screen than what is spoken.
  - "img" is a short, concrete visual search phrase for a stock photo site. It must ALWAYS depict a real finance/business/office scene (e.g. stock charts, cash, calculators, laptops with spreadsheets, bank buildings, people reviewing documents, coins, piggy banks) — NEVER depict an analogy literally (no kids, pizza, gardens, games, toys, animals). Follow the IMAGES MUST DIFFERENTIATE rule above — Term A slides and Term B slides need visually distinct imagery.
- Each analogy (for both terms) must be stated in one simple sentence a 10 year old would get instantly, BEFORE using the formal finance term.
- Do not literally write "SUBSCRIBE" as the whole slide 7 text — the app already adds a subscribe button automatically.
- Use specific, believable numbers (dollar amounts, percentages, timeframes) in the real-number example — never vague claims.
- Never mention any brand, bank, or app name that could be factually wrong or outdated; prefer generic terms like "a high-yield savings account".
- Great tags: "keywords" should include both term names plus 3-4 strong searchable finance tags.
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

    term_a, term_b = random.choice(CONFUSABLE_PAIRS)
    user_prompt = f"Write a new video differentiating these two confusable terms: \"{term_a}\" vs \"{term_b}\"."
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

    for model in GEMINI_MODEL_CANDIDATES:
        try:
            resp = requests.post(
                _gemini_url(model),
                params={"key": GEMINI_API_KEY},
                json=payload,
                timeout=45,
            )
            if resp.status_code != 200:
                print(f"[WARN] Gemini API error {resp.status_code} on {model}: {resp.text[:200]}")
                continue

            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            topic = _extract_json(raw_text)

            if not _validate_topic(topic):
                print(f"[WARN] Gemini ({model}) returned malformed topic")
                continue

            topic["term_a"] = term_a
            topic["term_b"] = term_b
            return topic

        except Exception as e:
            print(f"[WARN] Gemini generation failed on {model}: {e}")
            continue

    return None
