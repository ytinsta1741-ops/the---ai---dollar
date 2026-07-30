#!/usr/bin/env python3
"""
The AI Dollar - Video Generator
Finance education Shorts with cartoon/illustration backgrounds + animated zoom + deep male TTS
"""

import os
import gc
import subprocess
import asyncio
import requests
from datetime import datetime

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"✅ FFmpeg ready: {FFMPEG}")
except Exception as e:
    FFMPEG = "ffmpeg"
    print(f"⚠️ Using system ffmpeg: {e}")

CONFIG = {"output_dir": "./videos"}

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

CONTENT_TOPICS = [
    {
        "title": "What Inflation Actually Does to Your Money",
        "search_queries": [
            "coins stacked", "grocery shopping", "piggy bank",
            "wallet cash", "supermarket aisle", "savings money",
            "dollar bills", "shopping cart",
        ],
        "slides": [
            {"text": "What inflation\nactually does\nto your money", "duration": 3.5},
            {"text": "That $100 you saved\nlast year?", "duration": 3},
            {"text": "It now buys\nabout $93 worth\nof stuff", "duration": 3.5},
            {"text": "Your money did not\ndisappear", "duration": 2.5},
            {"text": "Prices just\nwent up", "duration": 2.5},
            {"text": "This is why keeping\ncash under your\nmattress hurts you", "duration": 3.5},
            {"text": "Your savings need\nto grow faster\nthan inflation", "duration": 3.5},
            {"text": "Thats the\nwhole game", "duration": 2.5},
        ],
        "voiceover": "Let me tell you something about inflation that nobody talks about. That hundred dollars you saved last year? Right now it only buys about ninety three dollars worth of stuff. Your money didn't disappear. Prices just went up around it. And this is exactly why keeping cash under your mattress is one of the worst things you can do. Your savings need to grow faster than inflation. That's the whole game. That's all personal finance comes down to.",
        "keywords": ["Inflation", "Finance", "Money"],
    },
    {
        "title": "Compound Interest Explained in 60 Seconds",
        "search_queries": [
            "plant growing", "stacked coins growth", "savings jar",
            "money growth", "tree growing", "investment growth",
            "calculator finance", "snowball rolling hill", "wealth building",
        ],
        "slides": [
            {"text": "Compound interest\nexplained in\n60 seconds", "duration": 3},
            {"text": "You put $1,000\nin an account", "duration": 3},
            {"text": "It earns 5 percent\na year", "duration": 2.5},
            {"text": "Year 1\nyou have $1,050", "duration": 3},
            {"text": "Year 2\nyou earn 5 percent\non $1,050", "duration": 3},
            {"text": "Not on $1,000", "duration": 2},
            {"text": "Your interest\nearns interest", "duration": 3},
            {"text": "In 30 years that\n$1,000 becomes\n$4,322", "duration": 3.5},
            {"text": "Without adding\na single dollar", "duration": 3},
        ],
        "voiceover": "Let me break down compound interest in sixty seconds flat. You put one thousand dollars in an account that earns five percent a year. After year one, you have one thousand and fifty. Now here's where it gets interesting. In year two, you earn five percent on one thousand and fifty. Not on the original thousand. Your interest starts earning its own interest. That's the magic of compounding. In thirty years, that one thousand turns into four thousand three hundred twenty two. Without you adding a single dollar. Start early. Time is the real cheat code.",
        "keywords": ["Compound Interest", "Investing", "Finance"],
    },
    {
        "title": "What Your Credit Score Actually Means",
        "search_queries": [
            "credit card hand", "bank building", "loan document",
            "house keys", "financial planning", "approved stamp",
            "mortgage house", "person paying bills",
        ],
        "slides": [
            {"text": "What your credit\nscore actually\nmeans", "duration": 3},
            {"text": "A number\nbetween 300\nand 850", "duration": 3},
            {"text": "Banks use it to\ndecide if they\ntrust you", "duration": 3.5},
            {"text": "Above 740?\nYou get the\nbest rates", "duration": 3},
            {"text": "Below 580?\nYou pay way\nmore in interest", "duration": 3.5},
            {"text": "On a $300,000\nmortgage bad\ncredit costs you\n$100,000 extra", "duration": 4},
            {"text": "Pay on time\nKeep balances low\nDo not close\nold cards", "duration": 4},
            {"text": "Three rules\nthats it", "duration": 2.5},
        ],
        "voiceover": "Your credit score. I bet most of you don't actually know what this number means. It goes from three hundred to eight fifty. Banks look at it to decide whether they trust you with their money. Got above seven forty? You're getting the absolute best interest rates out there. Below five eighty? You're paying way more than everyone else. On a three hundred thousand dollar mortgage, bad credit can cost you over a hundred thousand extra. How to keep it high? Pay on time. Keep your balances low. Don't close your oldest cards. Three rules. That's literally all there is to it.",
        "keywords": ["Credit Score", "Finance", "Banking"],
    },
    {
        "title": "The 50/30/20 Budget Rule",
        "search_queries": [
            "budget planning", "paycheck money", "rent apartment",
            "grocery bag", "shopping bag", "piggy bank savings",
            "financial planning desk", "calculator budget", "coins jar",
        ],
        "slides": [
            {"text": "The simplest\nbudget that\nactually works", "duration": 3},
            {"text": "Take your\npaycheck", "duration": 2},
            {"text": "50 percent goes\nto needs", "duration": 2.5},
            {"text": "Rent, food,\nutilities,\ntransportation", "duration": 3},
            {"text": "30 percent goes\nto wants", "duration": 2.5},
            {"text": "Eating out,\nentertainment,\nshopping", "duration": 3},
            {"text": "20 percent goes\nto savings", "duration": 2.5},
            {"text": "Emergency fund\nfirst, then\ninvesting", "duration": 3},
            {"text": "Simple?\nYes\nEffective?\nExtremely", "duration": 3},
        ],
        "voiceover": "I'm going to give you the simplest budget that actually works in real life. Take your paycheck. Fifty percent goes straight to needs. Rent, food, utilities, transportation. Thirty percent is for wants. Eating out, entertainment, a little shopping. And twenty percent goes directly into savings. Build your emergency fund first, then start investing what's left. Is it simple? Absolutely. Is it effective? Extremely. Most millionaires started with this exact formula. No fancy spreadsheets needed.",
        "keywords": ["Budgeting", "50/30/20", "Personal Finance"],
    },
    {
        "title": "Stocks vs Bonds - The Real Difference",
        "search_queries": [
            "stock market screen", "wall street", "business chart",
            "company building", "newspaper finance", "trading desk",
            "investment portfolio", "growth chart", "stock exchange",
        ],
        "slides": [
            {"text": "Stocks vs Bonds\nthe real\ndifference", "duration": 3},
            {"text": "A stock means\nyou own a tiny\npiece of a company", "duration": 3.5},
            {"text": "If the company\ngrows, your\nmoney grows", "duration": 3},
            {"text": "If it tanks,\nso does your\ninvestment", "duration": 3},
            {"text": "A bond means\nyou are lending\nmoney", "duration": 3},
            {"text": "To a government\nor company", "duration": 2.5},
            {"text": "They pay you\nback with interest", "duration": 3},
            {"text": "Lower risk\nlower reward", "duration": 2.5},
            {"text": "Young? More stocks\nOlder? More bonds", "duration": 3},
        ],
        "voiceover": "Stocks versus bonds. Let me clear this up once and for all. When you buy a stock, you own a tiny piece of a company. If that company grows, your money grows with it. But if it tanks, your investment goes down too. A bond is a completely different thing. You're basically lending money to a government or a company. They pay you back over time, with interest. Lower risk, but lower reward. Here's the general rule. If you're young, lean into stocks. You've got time to ride the ups and downs. As you get older, shift more into bonds for stability.",
        "keywords": ["Stocks", "Bonds", "Investing"],
    },
    {
        "title": "What an Emergency Fund Is and Why You Need One",
        "search_queries": [
            "car repair mechanic", "rainy day umbrella", "safety net",
            "broken car road", "money jar", "piggy bank",
            "hospital building", "wallet cash savings",
        ],
        "slides": [
            {"text": "Why you need an\nemergency fund", "duration": 3},
            {"text": "Your car breaks\ndown tomorrow", "duration": 2.5},
            {"text": "Repair costs\n$800", "duration": 2.5},
            {"text": "No emergency fund?\nThat goes on a\ncredit card", "duration": 3.5},
            {"text": "At 24 percent\ninterest", "duration": 2},
            {"text": "Now that $800\ncosts you $1,100", "duration": 3},
            {"text": "An emergency fund\nis 3 to 6 months\nof expenses", "duration": 3.5},
            {"text": "In a savings\naccount you\nnever touch", "duration": 3},
            {"text": "Not investing\nIts insurance", "duration": 3},
        ],
        "voiceover": "Listen, here's why you need an emergency fund. Picture this. Your car breaks down tomorrow. Repair costs eight hundred dollars. Without an emergency fund, that eight hundred goes straight onto a credit card. At twenty four percent interest, that repair just became eleven hundred dollars. An emergency fund is three to six months of your expenses, sitting in a savings account you don't touch. It's not investing. It's insurance. It's the difference between a rough week and a full blown financial disaster.",
        "keywords": ["Emergency Fund", "Savings", "Finance"],
    },
    {
        "title": "What Is a Recession",
        "search_queries": [
            "empty office", "closed store", "unemployment line",
            "stock chart down", "city skyline", "empty street",
            "business meeting", "economic recovery", "growth chart up",
            "people working",
        ],
        "slides": [
            {"text": "What is a\nrecession?", "duration": 2.5},
            {"text": "When the economy\nshrinks for 6+\nmonths straight", "duration": 3.5},
            {"text": "Companies make\nless money", "duration": 2.5},
            {"text": "They cut jobs", "duration": 2},
            {"text": "People spend less", "duration": 2},
            {"text": "Which means\ncompanies make\neven less", "duration": 3},
            {"text": "Its a cycle", "duration": 2},
            {"text": "But heres\nthe thing", "duration": 2},
            {"text": "Every single\nrecession in\nhistory ended", "duration": 3.5},
            {"text": "The economy\nalways recovered", "duration": 3},
        ],
        "voiceover": "What is a recession? Let me explain it simply. It's when the economy shrinks for six or more months in a row. Companies start making less money, so they cut jobs. People have less income, so they spend less. Which means companies make even less. It's a downward cycle that feeds itself. But here's the thing that most people forget in the moment. Every single recession in history has ended. Every one. The economy has always recovered. The absolute worst financial decision you can make during a recession is to panic.",
        "keywords": ["Recession", "Economy", "Finance"],
    },
    {
        "title": "Assets vs Liabilities",
        "search_queries": [
            "real estate house", "luxury car", "rental property",
            "investment chart", "house keys hand", "wallet money",
            "apartment building", "person saving money", "balance scale",
        ],
        "slides": [
            {"text": "Assets vs\nLiabilities", "duration": 2.5},
            {"text": "An asset puts\nmoney in\nyour pocket", "duration": 3},
            {"text": "A liability takes\nmoney out", "duration": 2.5},
            {"text": "Your house?\nIt depends", "duration": 2.5},
            {"text": "If you live in it\nit costs you\nmoney every month", "duration": 3.5},
            {"text": "Mortgage, taxes,\nmaintenance", "duration": 2.5},
            {"text": "If you rent it out\nand it makes\nmore than it costs", "duration": 3.5},
            {"text": "Now its\nan asset", "duration": 2.5},
            {"text": "Rich people buy\nassets first", "duration": 3},
        ],
        "voiceover": "Assets versus liabilities. Let me make this crystal clear. An asset puts money into your pocket. A liability takes money out. That's it. Your house? Well, it depends. If you live in it, it costs you money every single month. Mortgage, taxes, maintenance. That's a liability. But if you rent it out, and it brings in more money than it costs you, now it's an asset. The difference between wealthy people and everyone else? Wealthy people buy assets first. They let those assets pay for their lifestyle.",
        "keywords": ["Assets", "Liabilities", "Wealth"],
    },
]


def fetch_pexels_images(queries, num_images, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    images = []

    for i in range(num_images):
        query = queries[i % len(queries)]
        img_path = os.path.join(save_dir, f"slide_{i}.jpg")

        if os.path.exists(img_path):
            images.append(img_path)
            continue

        try:
            url = f"https://api.pexels.com/v1/search?query={query}&orientation=portrait&per_page=15&page=1"
            headers = {"Authorization": PEXELS_API_KEY}
            resp = requests.get(url, headers=headers, timeout=10)

            if resp.status_code == 200:
                data = resp.json()
                photos = data.get("photos", [])
                if photos:
                    photo = photos[i % len(photos)]
                    img_url = photo["src"].get("portrait", photo["src"]["large"])
                    img_resp = requests.get(img_url, timeout=15)
                    if img_resp.status_code == 200:
                        with open(img_path, 'wb') as f:
                            f.write(img_resp.content)
                        images.append(img_path)
                        print(f"  📸 Image {i+1}: {query}")
                        continue

            print(f"  ⚠️ Pexels {resp.status_code}: {resp.text[:150]}")
            images.append(None)

        except Exception as e:
            print(f"  ⚠️ Image error: {e}")
            images.append(None)

    return images


def create_audio(text, output_path):
    try:
        from silero_tts import silero_tts
        silero_tts(text, language='en', speaker='en_0', audio_path=output_path)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print("✅ Audio ready (Silero TTS - deep male voice)")
            return True
    except Exception as e:
        print(f"⚠️ Silero TTS failed ({e}), trying edge-tts...")
        try:
            import edge_tts
            for voice in ["en-US-GuyNeural", "en-US-ChristopherNeural", "en-US-AndrewNeural"]:
                try:
                    communicate = edge_tts.Communicate(text, voice, rate="-5%", pitch="-2Hz")
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(communicate.save(output_path))
                    loop.close()
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                        print(f"✅ Audio ready (voice: {voice})")
                        return True
                except Exception:
                    continue
            raise Exception("All voices blocked")
        except Exception as e2:
            print(f"⚠️ edge-tts failed ({e2}), using gTTS")
            from gtts import gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_path)
            print("✅ Audio ready (gTTS fallback)")
            return True


def get_audio_duration(audio_path):
    cmd = [FFMPEG, '-i', audio_path, '-f', 'null', '-']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, stderr = proc.communicate()
    output = stderr.decode('utf-8', errors='replace')
    for line in output.split('\n'):
        if 'Duration' in line:
            time_str = line.split('Duration:')[1].split(',')[0].strip()
            parts = time_str.split(':')
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return 25


def escape_ffmpeg_text(text):
    text = text.replace("'", "")
    text = text.replace(":", "\\:")
    text = text.replace("$", "\\$")
    text = text.replace("%", "%%")
    text = text.replace('"', "")
    text = text.replace(";", "\\;")
    return text


def prep_slides(images, slides, scale, work_dir):
    """Pre-render each slide as a JPEG with text burned in via Pillow (faster, better fonts)"""
    os.makedirs(work_dir, exist_ok=True)
    concat_file = os.path.join(work_dir, "concat.txt")

    from PIL import Image, ImageDraw, ImageFont

    def get_font(size):
        font_names = [
            "Arial Black.ttf", "ArialBD.ttf", "arial.ttf",
            "DejaVuSans-Bold.ttf", "FreeSansBold.ttf",
            "LiberationSans-Bold.ttf", "Ubuntu-Bold.ttf",
            "Helvetica-Bold"
        ]
        for name in font_names:
            try:
                return ImageFont.truetype(name, size)
            except Exception:
                continue
        try:
            import matplotlib
            font_path = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf", "DejaVuSans-Bold.ttf")
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass
        return ImageFont.load_default()

    title_font = get_font(52)
    body_font = get_font(46)

    for idx, slide in enumerate(slides):
        img_src = images[idx] if idx < len(images) else None
        out = os.path.join(work_dir, f"s_{idx}.jpg")

        if img_src and os.path.exists(img_src):
            bg = Image.open(img_src).convert("RGB")
            bg = bg.resize((720, 1280), Image.LANCZOS)
        else:
            bg = Image.new("RGB", (720, 1280), (10, 10, 46))

        overlay = Image.new("RGBA", (720, 1280), (0, 0, 0, 140))
        bg = bg.convert("RGBA")
        bg = Image.alpha_composite(bg, overlay).convert("RGB")
        del overlay

        draw = ImageDraw.Draw(bg)
        lines = slide['text'].split('\n')
        line_h = 75
        total_h = len(lines) * line_h
        start_y = max(100, (1280 - total_h) // 2)

        for li, line in enumerate(lines):
            font = title_font if li == 0 else body_font
            color = (255, 255, 255) if li == 0 else (100, 220, 255)
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = (720 - tw) // 2
            y = start_y + li * line_h

            for ox in [-3, -2, -1, 1, 2, 3]:
                for oy in [-3, -2, -1, 1, 2, 3]:
                    draw.text((x + ox, y + oy), line, font=font, fill=(0, 0, 0, 180))
            draw.text((x, y), line, font=font, fill=color)

        bg.save(out, "JPEG", quality=85)
        del draw, bg
        gc.collect()
        print(f"  slide {idx+1}/{len(slides)} ready")

    with open(concat_file, 'w') as f:
        for idx, slide in enumerate(slides):
            dur = slide['duration'] * scale
            f.write(f"file 's_{idx}.jpg'\n")
            f.write(f"duration {dur:.2f}\n")
        f.write(f"file 's_{len(slides)-1}.jpg'\n")

    return concat_file


def create_video_ffmpeg(slides, images, audio_file, output_file):
    audio_duration = get_audio_duration(audio_file)
    total_slide_dur = sum(s['duration'] for s in slides)
    scale = audio_duration / total_slide_dur if total_slide_dur > 0 else 1.0

    valid_images = [img for img in images if img is not None]
    if not valid_images:
        return create_video_simple(slides, audio_file, output_file)

    work_dir = output_file + "_work"
    print("🖼️ Preparing slides with text...")
    concat_file = prep_slides(images, slides, scale, work_dir)

    cmd = [
        FFMPEG, '-y',
        '-f', 'concat', '-safe', '0', '-i', concat_file,
        '-i', audio_file,
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
        '-c:a', 'aac', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        '-vsync', 'vfr',
        output_file
    ]

    print(f"🔧 Running FFmpeg (concat {len(slides)} slides)...")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        print("❌ FFmpeg timed out")
        return create_video_simple(slides, audio_file, output_file)

    import shutil
    shutil.rmtree(work_dir, ignore_errors=True)

    if proc.returncode != 0:
        err = stderr.decode('utf-8', errors='replace')[-500:]
        print(f"❌ FFmpeg failed: {err[-300:]}")
        return create_video_simple(slides, audio_file, output_file)

    print("✅ Video created with animated images!")
    return True


def create_video_simple(slides, audio_file, output_file):
    audio_duration = get_audio_duration(audio_file)
    total_slide_dur = sum(s['duration'] for s in slides)
    scale = audio_duration / total_slide_dur if total_slide_dur > 0 else 1.0

    filters = []

    t = 0
    for slide in slides:
        dur = slide['duration'] * scale
        lines = slide['text'].split('\n')
        num_lines = len(lines)
        start_y = f"(h/2)-{(num_lines * 30)}"

        for li, line in enumerate(lines):
            escaped = escape_ffmpeg_text(line)
            y_pos = f"({start_y})+{li * 60}"
            color = "white" if li == 0 else "0x00DDFF"
            filters.append(
                f"drawtext=text='{escaped}':"
                f"x=(w-text_w)/2:y={y_pos}:"
                f"fontsize=42:fontcolor={color}:"
                f"borderw=3:bordercolor=black:"
                f"enable='between(t,{t:.2f},{t+dur:.2f})'"
            )
        t += dur

    vf = ",".join(filters)
    cmd = [
        FFMPEG, '-y',
        '-f', 'lavfi', '-i', 'color=c=0x0A0A2E:size=720x1280:rate=24',
        '-i', audio_file,
        '-vf', vf,
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        output_file
    ]

    print(f"🔧 Running FFmpeg (simple mode)...")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(timeout=240)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        print("❌ FFmpeg timed out")
        return False

    if proc.returncode != 0:
        print(f"❌ FFmpeg failed")
        print(stderr.decode('utf-8', errors='replace')[-500:])
        return False

    print("✅ Video created (simple mode)")
    return True


def _get_next_topic_index():
    counter_file = "topic_counter.txt"
    try:
        if os.path.exists(counter_file):
            with open(counter_file) as f:
                idx = int(f.read().strip())
        else:
            idx = 0
    except Exception:
        idx = 0
    next_idx = (idx + 1) % len(CONTENT_TOPICS)
    with open(counter_file, "w") as f:
        f.write(str(next_idx))
    return idx


def generate_daily_video():
    index = _get_next_topic_index()
    topic = CONTENT_TOPICS[index]

    os.makedirs(CONFIG['output_dir'], exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = f"{CONFIG['output_dir']}/the_ai_dollar_{timestamp}.mp4"
    audio_file = f"{CONFIG['output_dir']}/audio_{timestamp}.mp3"
    img_dir = f"{CONFIG['output_dir']}/imgs_{timestamp}"

    try:
        print("🎤 Generating voiceover...")
        create_audio(topic['voiceover'], audio_file)

        images = []
        if PEXELS_API_KEY:
            print("📸 Fetching images from Pexels...")
            images = fetch_pexels_images(
                topic['search_queries'],
                len(topic['slides']),
                img_dir
            )
            print(f"✅ Got {sum(1 for i in images if i)} images")
        else:
            print("⚠️ No PEXELS_API_KEY, using color background")

        print("🎬 Creating animated video...")
        ok = create_video_ffmpeg(topic['slides'], images, audio_file, output_file)

        if not ok:
            return {"status": "error", "message": "Video creation failed"}

        print(f"✅ Video created: {output_file}")

        try:
            os.remove(audio_file)
        except Exception:
            pass
        try:
            import shutil
            shutil.rmtree(img_dir, ignore_errors=True)
        except Exception:
            pass

        return {
            "status": "success",
            "video": output_file,
            "title": topic['title'],
            "script": topic['voiceover'],
            "keywords": topic['keywords']
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
