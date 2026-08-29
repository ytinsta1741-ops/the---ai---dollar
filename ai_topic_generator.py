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

# 60-day curriculum, ordered into six 10-day thematic sprints. Running a
# consistent theme for ten days straight gives the platform a coherent
# topic signal to categorise the channel against, instead of the scattered
# signal that random topic order produces. Falls through to the wider pool
# below once all 60 are used.
CURRICULUM = [
    # Days 1-10 — Corporate Wealth & Business Mistakes
    ("revenue", "profit"),
    ("gross profit", "net profit"),
    ("cash flow", "profit"),
    ("markup", "margin"),
    ("gross margin", "net margin"),
    ("fixed cost", "variable cost"),
    ("assets", "revenue"),
    ("liability", "expense"),
    ("working capital", "fixed capital"),
    ("liquidity", "solvency"),
    # Days 11-20 — Investing & The Stock Market Mechanics
    ("stocks", "shares"),
    ("bonds", "stocks"),
    ("ETF", "mutual fund"),
    ("index fund", "mutual fund"),
    ("dividend", "capital gains"),
    ("realized gain", "unrealized gain"),
    ("market cap", "enterprise value"),
    ("bull market", "bear market"),
    ("dividend yield", "dividend rate"),
    ("stock split", "reverse split"),
    # Days 21-30 — Personal Finance & Banking Survival
    ("APR", "APY"),
    ("debit card", "credit card"),
    ("credit score", "credit report"),
    ("hard inquiry", "soft inquiry"),
    ("simple interest", "compound interest"),
    ("secured loan", "unsecured loan"),
    ("overdraft", "loan"),
    ("credit limit", "available credit"),
    ("checking account", "savings account"),
    ("prequalified", "preapproved"),
    # Days 31-40 — Macroeconomics & Global Systems
    ("inflation", "deflation"),
    ("recession", "depression"),
    ("fixed rate", "variable rate"),
    ("nominal value", "market value"),
    ("wholesale price", "retail price"),
    ("interest rate", "APR"),
    ("wire transfer", "ACH transfer"),
    ("commodity", "security"),
    ("private equity", "venture capital"),
    ("IPO", "direct listing"),
    # Days 41-50 — Tax Strategies & Corporate Secrets
    ("tax deduction", "tax credit"),
    ("standard deduction", "itemized deduction"),
    ("W-2", "1099"),
    ("gross pay", "take-home pay"),
    ("gross income", "net income"),
    ("depreciation", "amortization"),
    ("capital expenditure", "operating expenditure"),
    ("HSA", "FSA"),
    ("401k", "IRA"),
    ("Roth IRA", "Traditional IRA"),
    # Days 51-60 — Highest-search recap set (the concepts with the
    # strongest standing search demand, revisited to consolidate ranking)
    ("net worth", "net income"),
    ("cash flow", "net worth"),
    ("principal", "interest"),
    ("mortgage", "personal loan"),
    ("down payment", "deposit"),
    ("escrow", "equity"),
    ("term insurance", "whole life insurance"),
    ("premium", "deductible"),
    ("annuity", "pension"),
    ("leasing", "financing"),
]

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
    # expanded pool so a fresh pair is available far longer before any repeat
    ("ETF", "mutual fund"), ("index fund", "mutual fund"), ("HSA", "FSA"),
    ("401k", "IRA"), ("annuity", "pension"), ("leasing", "financing"),
    ("gross income", "net income"), ("assets", "revenue"), ("liability", "expense"),
    ("credit score", "credit report"), ("hard inquiry", "soft inquiry"),
    ("prequalified", "preapproved"), ("fixed rate", "variable rate"),
    ("down payment", "deposit"), ("principal", "interest"), ("escrow", "equity"),
    ("bear", "correction"), ("dividend yield", "dividend rate"),
    ("market cap", "enterprise value"), ("EBITDA", "net income"),
    ("realized gain", "unrealized gain"), ("liquidity", "solvency"),
    ("cash", "capital"), ("budget", "forecast"), ("audit", "review"),
    ("gross margin", "net margin"), ("markdown", "discount"),
    ("chargeback", "refund"), ("wire transfer", "ACH transfer"),
    ("checking account", "savings account"), ("APR", "interest rate"),
    ("term deposit", "demand deposit"), ("bond yield", "coupon rate"),
    ("face value", "market value"), ("premium", "deductible"),
    ("copay", "coinsurance"), ("underwriting", "appraisal"),
    ("refinance", "consolidation"), ("grace period", "introductory period"),
    ("standard deduction", "itemized deduction"), ("W-2", "1099"),
    ("gross pay", "take-home pay"), ("credit limit", "available credit"),
    ("bull trap", "dead cat bounce"), ("stock split", "reverse split"),
    ("IPO", "direct listing"), ("private equity", "venture capital"),
    ("hedge fund", "mutual fund"), ("commodity", "security"),
]

SYSTEM_PROMPT = """You are an expert financial educator and content creator writing scripts for "The AI Dollar", a YouTube Shorts channel. Every video takes TWO real finance or accounting terms that people genuinely confuse with each other (you'll be given the pair, e.g. "loan" vs "debenture") and clearly differentiates them for a complete beginner — the way you'd explain it to a smart 10 year old, using simple real-world analogies, not a lecture. Explain any abbreviation in full the first time it appears.

HARD LENGTH LIMIT — the "speech" text across ALL 7 slides combined must total 75 WORDS OR FEWER. This is the single most important constraint: at the channel's 1.15x delivery that lands the video at 25-28 seconds, which is where retention holds. Count the words before you answer. If you are over 75, cut adjectives and whole sentences until you are under — never pad to fill slides. A slide may be as short as four words.

TEACH WITH A HUMAN CASE STUDY, NEVER A DEFINITION. Do not write dictionary lines like "Net worth is assets minus liabilities" — that gets swiped past instantly. Instead build the whole video around TWO NAMED PEOPLE placed side by side, one embodying each term, with a polarising contrast: the one who LOOKS rich but is quietly going broke, versus the one who looks ordinary but is genuinely building wealth. Invent ordinary first names (Marcus, Dana, Priya, Jordan). Give them concrete jobs and real dollar figures. The viewer should learn the difference by watching two lives diverge, not by being told a rule.

STRUCTURE — every video follows this arc across the 7 slides:
1. Hook (first 4 seconds — this single line decides whether the video dies). It MUST create an immediate contradiction the viewer needs resolved. Build it from a concrete PERSON and a number that shouldn't go together, and state it flat, like an accusation. Aim for one of these shapes:
   - Contradiction: "He earns triple her salary. She's the rich one."
   - Proximity + stakes: "Two owners. Same street. One is bleeding cash."
   - Reversal: "His business made two million. He took home nothing."
   - Accusation: "Your paycheck is lying to you."
   BANNED hook openings, they kill retention instantly: any question ("Do you know...", "Ever wondered..."), any definition, any greeting, any use of the words "let's", "today", "in this video", and naming the two finance terms in the first sentence. Name the PEOPLE and the NUMBERS first — the terms themselves are revealed later, once the viewer is already invested in the outcome.
2. Person A introduced — their job, their impressive-looking number.
3. What is actually draining Person A — the hidden cost, with figures.
4. Person B introduced — the unglamorous job, the smaller number.
5. What Person B actually keeps — the figures that reveal the truth.
6. The one-line verdict naming both terms explicitly and which person has which.
7. LOOP CLOSER: end MID-THOUGHT on a cliffhanger that runs straight back into the first words of slide 1, so the video loops seamlessly. End on "because…", "and that's when…", "which means…". NEVER end with "subscribe", "follow for more", or any sign-off — the app adds its own end card.

FORBIDDEN: introductory phrases ("Hey guys", "Welcome back", "Let's talk about") and concluding phrases ("Subscribe", "Follow for more", "Thanks for watching"). Open cold on the hook, end mid-sentence on the loop.

IMAGES MUST DIFFERENTIATE THE TWO TERMS. Slides about Term A need a DIFFERENT image concept than slides about Term B — e.g. if comparing "loan" vs "debenture", a loan slide might show a bank loan officer or a person signing paperwork at a bank, while a debenture slide shows a bond certificate or investment document — visually distinct so the viewer's eye associates a different picture with each term. Never reuse the same visual concept for both terms.

When a slide's example or analogy naturally involves a well-known finance/business figure (e.g. explaining equity/investing with Warren Buffett, the Federal Reserve with Jerome Powell, entrepreneurship with Elon Musk or Jeff Bezos), you may set "img" to just that person's exact full name instead of a scene description — the app will fetch an appropriately licensed photo. Only use figures from this safe list: Warren Buffett, Jerome Powell, Elon Musk, Jeff Bezos, Bill Gates, Mark Cuban, Janet Yellen, Ray Dalio, Charlie Munger. Do not invent other names.

FRAME THE TITLE around the confusion itself, not a flat definition. Real audience data on this channel confirms two hook styles clearly outperform plain "What is X" videos:
- CONFUSION-CALLOUT: "You've Been Mixing Up [A] and [B] — Here's The Difference", "[A] vs [B]: The Difference Nobody Explains"
- PERSONAL-STAKES QUESTION: "Do You Actually Know The Difference Between [A] and [B]?", "Is Confusing These Two Costing You Money?" — this style has been the single best-performing hook on this channel so far.
- The title must always promise clarity on a real confusion — never a plain definition.

VOICE: Explain it like you're talking to a smart 10 year old who's never heard either word before — not like you're reading a dictionary entry. Be VERY compact. Concretely:
- REGISTER: write like a dark-mode investigative documentary narrator or a high-status financial investigator delivering a verdict — cold, authoritative, slightly ominous. Not chirpy, not a teacher, not a friend.
- Reach for raw power words where they fit honestly: trapped, illusion, bankrupt, drained, bleeding cash, quietly, vanishes, collapse.
- Max 2 short sentences per slide. Never more than ~10 words per sentence. Short declaratives with hard full stops — "Rent. Staff. Suppliers. Eighty-eight thousand gone." Sharp punctuation gives text-to-speech clean breaks and zero awkward pauses.
- One idea per slide, always.
- Contractions where natural — never stiff or academic phrasing.
- Zero filler, zero throat-clearing ("So basically...", "Let's dive in..."). Start every sentence already saying something.
- If you'd have to explain a word you just used, you used the wrong word — replace it with a simpler one.
- Numbers must be written as words in "speech" so text-to-speech reads them cleanly ("ninety thousand", not "$90,000"), but may stay as digits in the on-screen "text".

Rules:
- Output ONLY valid JSON, no markdown fences, no commentary.
- Exactly 7 slides.
- Every slide has "text", "speech", and "img":
  - "speech" is what the narrator says out loud, 1-3 short punchy spoken sentences (see VOICE above), energetic and conversational, never lecture-toned.
  - "text" is the on-screen caption — the SINGLE punchiest phrase from that slide's speech, and it MUST be tiny: AT MOST 2 short lines, no more than 3-4 words per line (~20 characters per line). Pick only the 3-6 most important words so a viewer reads it in one glance — never a full sentence, never a paragraph. Separate the two lines with \\n. Every word must also appear in that slide's "speech".
  - "img" describes the photograph shown while that slide's SPEECH is heard. It must depict the specific thing that slide is actually talking about — if the speech says a restaurant grosses ninety thousand a month, show a busy restaurant dining room or a till roll, not a generic office. A viewer who muted the sound should still know which idea is on screen. It must ALWAYS be a real finance/business/office subject (stock charts on a monitor, banknotes, coins, calculators, laptops with spreadsheets, bank buildings, ledgers, contracts on a desk, shop interiors) — NEVER depict an analogy literally (no kids, pizza, gardens, games, toys, animals). Follow the IMAGES MUST DIFFERENTIATE rule above — Term A slides and Term B slides need visually distinct imagery.
  - NO PEOPLE IN "img". Never describe a person, face, hand, finger, or any body part. The image generator renders hands as fused, melted lumps and faces as distorted, which looks broken and unprofessional. Describe the OBJECTS and the PLACE instead, with nobody in frame: write "a mortgage contract and house keys on a desk" — never "hands signing a mortgage"; write "an empty restaurant dining room at closing time" — never "an owner counting cash". The one exception is the named-public-figure rule below, which uses real licensed photographs rather than generated images.
- Each analogy (for both terms) must be stated in one simple sentence a 10 year old would get instantly, BEFORE using the formal finance term.
- Do not literally write "SUBSCRIBE" as the whole slide 7 text — the app already adds a subscribe button automatically.
- Use specific, believable numbers (dollar amounts, percentages, timeframes) in the real-number example — never vague claims.
- Never mention any brand, bank, or app name that could be factually wrong or outdated; prefer generic terms like "a high-yield savings account".
- Great tags: "keywords" should include both term names plus 3-4 strong searchable finance tags.
- "icon_a" and "icon_b" name the CONCRETE OBJECT that will be illustrated on each side of the comparison panel — one for the first term, one for the second. These must be physical, drawable things, never abstractions: an image generator cannot draw "revenue" or "liquidity", but it can draw "a cash register overflowing with banknotes" or "a running tap pouring coins into a glass bowl". Pick objects that are instantly readable at a glance and clearly DIFFERENT from each other, so the two panels never look alike. Two or three plain words plus a short qualifier, e.g. "a stack of gold coins with an upward arrow" / "a red bill invoice with a chain and padlock". No text, letters or numbers in the described object. NO PEOPLE, HANDS, FACES OR BODY PARTS — the same rule as "img" above, and for the same reason: generated hands come out fused and melted. An object on its own always beats an object being held.
- Output JSON shape exactly:
{"title": "...", "keywords": ["...", "...", "..."], "icon_a": "...", "icon_b": "...", "slides": [{"text": "...", "speech": "...", "img": "..."}, ... exactly 7 objects]}
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

    # Enforce the script length limit rather than trusting the model to
    # honour it — an over-long script pushes the video past the ~28s where
    # retention drops off. A little slack over the stated 75 so we don't
    # throw away otherwise-good scripts on a word or two.
    words = sum(len(s["speech"].split()) for s in data["slides"])
    if words > 85:
        print(f"[WARN] Script too long ({words} words, limit 85) — regenerating")
        return False

    if not data.get("keywords"):
        data["keywords"] = [data["title"].split()[0], "Personal Finance", "Money Tips"]
    return True


# Pairs already used — cycles through the whole pool before any pair repeats.
# NOT just in-memory: Render wipes memory on every redeploy (which happens
# often), so a purely in-memory set silently resets and repeats start
# happening again right after any push. sync_used_pairs_from_titles() rebuilds
# this from the channel's REAL YouTube upload history at startup instead —
# that's the only state that actually survives a redeploy.
_used_pairs = set()


def sync_used_pairs_from_titles(titles):
    """Scan real posted titles for which CONFUSABLE_PAIRS they cover (both
    term names appear in the title, case-insensitive) and mark those used.
    Called from topic_generator.py's YouTube history sync at every startup."""
    added = 0
    for title in titles:
        low = title.lower()
        for pair in CONFUSABLE_PAIRS:
            if pair in _used_pairs:
                continue
            a, b = pair
            if a.lower() in low and b.lower() in low:
                _used_pairs.add(pair)
                added += 1
    if added:
        print(f"[OK] Synced {added} confusable pairs as already-used from YouTube history")


def _pick_unused_pair():
    # Work through the 60-day curriculum in order first — early uploads
    # should hit the highest-search-intent terms rather than a random pick —
    # then fall back to the wider pool once the curriculum is exhausted.
    for pair in CURRICULUM:
        if pair not in _used_pairs:
            _used_pairs.add(pair)
            return pair

    remaining = [p for p in CONFUSABLE_PAIRS if p not in _used_pairs]
    if not remaining:            # whole pool exhausted -> start a fresh cycle
        _used_pairs.clear()
        remaining = list(CONFUSABLE_PAIRS)
    pair = random.choice(remaining)
    _used_pairs.add(pair)
    return pair


def generate_ai_topic(existing_titles_hint=""):
    """Ask Gemini for one complete 7-slide short-form topic. Returns None on any failure."""
    if not GEMINI_API_KEY:
        print("[WARN] GEMINI_API_KEY not set, skipping AI generation")
        return None

    term_a, term_b = _pick_unused_pair()
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
