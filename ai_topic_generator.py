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
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

TOPIC_ANGLES = [
    "a specific money-saving challenge with real weekly numbers",
    "a myth about investing or saving that most people believe and get wrong",
    "a lesser-known finance strategy or account type used by wealthy people",
    "a comparison of two ways to build wealth, with real dollar numbers",
    "a step-by-step plan someone can follow starting today to build an emergency fund",
    "a breakdown of what a confusing finance term actually means in plain English",
    "a side-hustle or income idea with real monthly earnings numbers",
    "a rule the rich follow that broke people usually ignore",
    "a story about a normal person who built wealth slowly through one habit",
    "the true cost of a small daily expense over 10-30 years if invested instead",
]

SYSTEM_PROMPT = """You write scripts for "The AI Dollar", a YouTube Shorts channel that teaches personal finance to complete beginners in a punchy, hook-driven style.

Rules:
- Output ONLY valid JSON, no markdown fences, no commentary.
- Exactly 7 slides.
- Every slide has: "text" (what appears on screen, 3-5 short lines separated by \\n, ALL CAPS words for emphasis are fine, max ~40 characters per line), "speech" (what the narrator says out loud for that slide, 1-3 natural spoken sentences, energetic tone), and "img" (a short, concrete, literal visual search phrase for a stock photo site — describe a real scene/person/object, e.g. "person counting cash at kitchen table", NOT abstract ideas like "financial freedom" or "growth mindset").
- The "speech" and "img" for each slide MUST describe the same concrete scene — never mismatch them.
- If you use ANY finance jargon or technical term (e.g. "amortization", "arbitrage", "debenture", "index fund", "REIT", "compound interest"), you MUST immediately explain it in the same slide's speech using a simple one-sentence real-world analogy a 12 year old would understand. Never leave a technical term unexplained.
- Slide 1 is the hook — must create curiosity or shock in the first sentence.
- Slide 7 is the ending — recap the core lesson and tell the viewer to follow for more (do not literally write "SUBSCRIBE" as the whole slide, the app already adds a subscribe button automatically).
- Use specific, believable numbers (dollar amounts, percentages, ages, timeframes) — never vague claims.
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

    angle = random.choice(TOPIC_ANGLES)
    user_prompt = f"Write a new video about: {angle}."
    if existing_titles_hint:
        user_prompt += f" Make it clearly different from these already-posted titles: {existing_titles_hint}."

    payload = {
        "contents": [{"parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "generationConfig": {
            "temperature": 1.1,
            "maxOutputTokens": 1500,
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
