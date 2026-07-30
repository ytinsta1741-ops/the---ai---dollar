#!/usr/bin/env python3
"""
The AI Dollar - Video Generator
Finance education Shorts with stock images + deep male TTS voiceover
"""

import os
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
        "search_queries": ["grocery shopping", "price tag store", "wallet money", "supermarket aisle", "cost of living", "empty wallet", "rising prices"],
        "slides": [
            {"text": "What inflation\nactually does\nto your money", "duration": 3.5},
            {"text": "That $100 you saved\nlast year?", "duration": 3},
            {"text": "It now buys\nabout $93 worth\nof stuff", "duration": 3.5},
            {"text": "Your money didn't\ndisappear", "duration": 2.5},
            {"text": "Prices just\nwent up", "duration": 2.5},
            {"text": "This is why keeping\ncash under your\nmattress hurts you", "duration": 3.5},
            {"text": "Your savings need\nto grow faster\nthan inflation", "duration": 3.5},
            {"text": "That's the\nwhole game", "duration": 2.5},
        ],
        "voiceover": "Let's talk about what inflation actually does to your money. That hundred dollars you saved last year? It now buys about ninety three dollars worth of stuff. Your money didn't disappear. Prices just went up. This is why keeping cash under your mattress actually hurts you over time. Your savings need to grow faster than inflation. That's the whole game of personal finance right there.",
        "keywords": ["Inflation", "Finance", "Money"],
    },
    {
        "title": "Compound Interest Explained in 60 Seconds",
        "search_queries": ["money growing", "plant growing", "savings account", "piggy bank", "investment growth", "calculator finance", "bank interest"],
        "slides": [
            {"text": "Compound interest\nexplained in\n60 seconds", "duration": 3},
            {"text": "You put $1,000\nin an account", "duration": 3},
            {"text": "It earns 5%\na year", "duration": 2.5},
            {"text": "Year 1:\nyou have $1,050", "duration": 3},
            {"text": "Year 2:\nyou earn 5%\non $1,050", "duration": 3},
            {"text": "Not on $1,000", "duration": 2},
            {"text": "Your interest\nearns interest", "duration": 3},
            {"text": "In 30 years that\n$1,000 becomes\n$4,322", "duration": 3.5},
            {"text": "Without adding\na single dollar", "duration": 3},
        ],
        "voiceover": "Compound interest, explained simply. You put one thousand dollars in an account. It earns five percent a year. After year one, you have one thousand and fifty dollars. In year two, you earn five percent on one thousand and fifty, not on the original thousand. Your interest earns interest. That's compounding. In thirty years, that one thousand dollars becomes four thousand three hundred and twenty two dollars. Without you adding a single dollar. Start early. Time is the cheat code.",
        "keywords": ["Compound Interest", "Investing", "Finance"],
    },
    {
        "title": "What Your Credit Score Actually Means",
        "search_queries": ["credit card", "financial document", "loan application", "bank approval", "credit report", "financial planning", "mortgage house"],
        "slides": [
            {"text": "What your credit\nscore actually\nmeans", "duration": 3},
            {"text": "It's a number\nbetween 300\nand 850", "duration": 3},
            {"text": "Banks use it to\ndecide if they\ntrust you", "duration": 3.5},
            {"text": "Above 740?\nYou get the\nbest rates", "duration": 3},
            {"text": "Below 580?\nYou'll pay way\nmore in interest", "duration": 3.5},
            {"text": "On a $300,000\nmortgage, bad\ncredit costs you\n$100,000 extra", "duration": 4},
            {"text": "Pay on time\nKeep balances low\nDon't close\nold cards", "duration": 4},
            {"text": "Three rules\nthat's it", "duration": 2.5},
        ],
        "voiceover": "Your credit score. Most people don't really understand what it means. It's a number between three hundred and eight fifty. Banks use it to decide if they trust you with money. Above seven forty? You're getting the best interest rates available. Below five eighty? You're going to pay way more in interest. On a three hundred thousand dollar mortgage, bad credit can cost you over a hundred thousand dollars extra over the life of the loan. Here's how to keep it high. Pay on time. Keep your balances low. And don't close your old cards. Three rules. That's literally it.",
        "keywords": ["Credit Score", "Finance", "Banking"],
    },
    {
        "title": "The 50/30/20 Budget Rule",
        "search_queries": ["budget planning", "calculator notepad", "monthly bills", "savings jar", "financial planning desk", "paycheck money", "household budget"],
        "slides": [
            {"text": "The simplest\nbudget that\nactually works", "duration": 3},
            {"text": "Take your\npaycheck", "duration": 2},
            {"text": "50% goes to\nneeds", "duration": 2.5},
            {"text": "Rent, food,\nutilities,\ntransportation", "duration": 3},
            {"text": "30% goes to\nwants", "duration": 2.5},
            {"text": "Eating out,\nentertainment,\nshopping", "duration": 3},
            {"text": "20% goes to\nsavings", "duration": 2.5},
            {"text": "Emergency fund\nfirst, then\ninvesting", "duration": 3},
            {"text": "Simple?\nYes\nEffective?\nExtremely", "duration": 3},
        ],
        "voiceover": "Here's the simplest budget that actually works. Take your paycheck. Fifty percent goes to needs. That's rent, food, utilities, transportation. Thirty percent goes to wants. Eating out, entertainment, shopping. And twenty percent goes straight to savings. Build your emergency fund first, then start investing. Is it simple? Yes. Is it effective? Extremely. Most millionaires started with this exact formula.",
        "keywords": ["Budgeting", "50/30/20", "Personal Finance"],
    },
    {
        "title": "Stocks vs Bonds - What's the Difference",
        "search_queries": ["stock market screen", "wall street", "trading chart", "investment portfolio", "business newspaper", "financial graph", "stock exchange"],
        "slides": [
            {"text": "Stocks vs Bonds\nthe real\ndifference", "duration": 3},
            {"text": "A stock means\nyou own a tiny\npiece of a company", "duration": 3.5},
            {"text": "If the company\ngrows, your\nmoney grows", "duration": 3},
            {"text": "If it tanks,\nso does your\ninvestment", "duration": 3},
            {"text": "A bond means\nyou're lending\nmoney", "duration": 3},
            {"text": "To a government\nor company", "duration": 2.5},
            {"text": "They pay you\nback with interest", "duration": 3},
            {"text": "Lower risk\nlower reward", "duration": 2.5},
            {"text": "Young? More stocks\nOlder? More bonds", "duration": 3},
        ],
        "voiceover": "Stocks versus bonds. Here's the real difference. When you buy a stock, you own a tiny piece of a company. If the company grows, your money grows with it. But if it tanks, so does your investment. A bond is completely different. You're lending money to a government or a company. They pay you back with interest over time. Lower risk, but lower reward. General rule? If you're young, lean more into stocks. You have time to ride out the ups and downs. As you get older, shift more into bonds for stability.",
        "keywords": ["Stocks", "Bonds", "Investing"],
    },
    {
        "title": "What an Emergency Fund Is and Why You Need One",
        "search_queries": ["emergency savings", "rainy day", "broken car", "hospital bills", "piggy bank savings", "money jar", "financial safety"],
        "slides": [
            {"text": "Why you need an\nemergency fund", "duration": 3},
            {"text": "Your car breaks\ndown tomorrow", "duration": 2.5},
            {"text": "Repair costs\n$800", "duration": 2.5},
            {"text": "No emergency fund?\nThat goes on a\ncredit card", "duration": 3.5},
            {"text": "At 24% interest", "duration": 2},
            {"text": "Now that $800\ncosts you $1,100", "duration": 3},
            {"text": "An emergency fund\nis 3 to 6 months\nof expenses", "duration": 3.5},
            {"text": "In a savings\naccount you\ndon't touch", "duration": 3},
            {"text": "It's not investing\nIt's insurance", "duration": 3},
        ],
        "voiceover": "Here's why you need an emergency fund. Imagine your car breaks down tomorrow. The repair costs eight hundred dollars. If you don't have an emergency fund, that goes on a credit card. At twenty four percent interest, that eight hundred dollar repair now costs you eleven hundred. An emergency fund is three to six months of your expenses, sitting in a savings account you don't touch. It's not investing. It's insurance. It's the difference between a bad week and a financial disaster.",
        "keywords": ["Emergency Fund", "Savings", "Finance"],
    },
    {
        "title": "What Is a Recession",
        "search_queries": ["economic downturn", "stock market crash", "unemployment line", "closed business", "financial crisis", "recession economy", "market decline"],
        "slides": [
            {"text": "What is a\nrecession?", "duration": 2.5},
            {"text": "When the economy\nshrinks for 6+\nmonths straight", "duration": 3.5},
            {"text": "Companies make\nless money", "duration": 2.5},
            {"text": "They cut jobs", "duration": 2},
            {"text": "People spend less", "duration": 2},
            {"text": "Which means\ncompanies make\neven less", "duration": 3},
            {"text": "It's a cycle", "duration": 2},
            {"text": "But here's\nthe thing", "duration": 2},
            {"text": "Every single\nrecession in\nhistory ended", "duration": 3.5},
            {"text": "The economy\nalways recovered", "duration": 3},
        ],
        "voiceover": "What is a recession? It's when the economy shrinks for six or more months in a row. Companies make less money, so they cut jobs. People have less income, so they spend less. Which means companies make even less. It's a downward cycle. But here's the thing most people forget. Every single recession in history has ended. The economy has always recovered. Always. The worst financial decision you can make during a recession is panic.",
        "keywords": ["Recession", "Economy", "Finance"],
    },
    {
        "title": "Assets vs Liabilities",
        "search_queries": ["real estate investment", "luxury car", "rental property", "stock portfolio", "expensive watch", "house keys", "investment property"],
        "slides": [
            {"text": "Assets vs\nLiabilities", "duration": 2.5},
            {"text": "An asset puts\nmoney in\nyour pocket", "duration": 3},
            {"text": "A liability takes\nmoney out", "duration": 2.5},
            {"text": "Your house?\nIt depends", "duration": 2.5},
            {"text": "If you live in it\nit costs you\nmoney every month", "duration": 3.5},
            {"text": "Mortgage, taxes,\nmaintenance", "duration": 2.5},
            {"text": "If you rent it out\nand it makes\nmore than it costs", "duration": 3.5},
            {"text": "Now it's\nan asset", "duration": 2.5},
            {"text": "Rich people buy\nassets first", "duration": 3},
        ],
        "voiceover": "Assets versus liabilities. An asset puts money in your pocket. A liability takes money out. Simple. Your house? Well, it depends. If you live in it, it costs you money every month. Mortgage, taxes, maintenance. That's a liability. But if you rent it out, and it brings in more than it costs, now it's an asset. The difference between wealthy people and everyone else? Wealthy people buy assets first. They let those assets pay for their liabilities.",
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
            url = f"https://api.pexels.com/v1/search?query={query}&orientation=portrait&per_page=5&page=1"
            headers = {"Authorization": PEXELS_API_KEY}
            resp = requests.get(url, headers=headers, timeout=10)

            if resp.status_code == 200:
                data = resp.json()
                photos = data.get("photos", [])
                if photos:
                    photo = photos[i % len(photos)]
                    img_url = photo["src"]["large"]
                    img_resp = requests.get(img_url, timeout=15)
                    if img_resp.status_code == 200:
                        with open(img_path, 'wb') as f:
                            f.write(img_resp.content)
                        images.append(img_path)
                        print(f"  📸 Image {i+1}: {query}")
                        continue

            print(f"  ⚠️ Pexels API {resp.status_code}: {resp.text[:200]}")
            images.append(None)

        except Exception as e:
            print(f"  ⚠️ Image fetch error: {e}")
            images.append(None)

    return images


def create_audio(text, output_path):
    """Generate TTS audio using edge-tts (deep male voice)"""
    try:
        import edge_tts
        voice = "en-US-GuyNeural"
        communicate = edge_tts.Communicate(text, voice, rate="-5%", pitch="-2Hz")
        asyncio.run(communicate.save(output_path))
        print(f"✅ Audio ready (voice: {voice})")
        return True
    except Exception as e:
        print(f"⚠️ edge-tts failed ({e}), falling back to gTTS")
        from gtts import gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)
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
    return text.replace("'", "\\'").replace(":", "\\:").replace("$", "\\$").replace("%", "%%")


def create_video_ffmpeg(slides, images, audio_file, output_file):
    audio_duration = get_audio_duration(audio_file)
    total_slide_dur = sum(s['duration'] for s in slides)
    scale = audio_duration / total_slide_dur if total_slide_dur > 0 else 1.0

    valid_images = [img for img in images if img is not None]

    if not valid_images:
        return create_video_simple(slides, audio_file, output_file)

    input_args = []
    filter_parts = []

    for idx, img in enumerate(images):
        if img and os.path.exists(img):
            input_args.extend(['-i', img])
        else:
            input_args.extend(['-f', 'lavfi', '-i', 'color=c=0x0A0A2E:size=1080x1920:rate=30:d=0.1'])

    num_inputs = len(images)
    t = 0
    segments = []

    for idx, slide in enumerate(slides):
        dur = slide['duration'] * scale
        inp_idx = idx if idx < num_inputs else idx % num_inputs

        seg_label = f"seg{idx}"
        dark_label = f"dark{idx}"
        filter_parts.append(
            f"[{inp_idx}:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,setsar=1,loop=loop={int(dur*30)}:size=1:start=0,"
            f"fps=30,trim=duration={dur:.2f},setpts=PTS-STARTPTS[{seg_label}]"
        )
        filter_parts.append(
            f"[{seg_label}]drawbox=x=0:y=0:w=1080:h=1920:color=black@0.5:t=fill[{dark_label}]"
        )
        segments.append(f"[{dark_label}]")
        t += dur

    concat_inputs = "".join(segments)
    filter_parts.append(
        f"{concat_inputs}concat=n={len(slides)}:v=1:a=0[slideshow]"
    )

    text_filters = []
    t = 0
    for slide in slides:
        dur = slide['duration'] * scale
        lines = slide['text'].split('\n')
        num_lines = len(lines)
        start_y = f"(h/2)-{(num_lines * 35)}"

        for li, line in enumerate(lines):
            escaped = escape_ffmpeg_text(line)
            y_pos = f"({start_y})+{li * 70}"
            color = "white" if li == 0 else "0x00DDFF"
            text_filters.append(
                f"drawtext=text='{escaped}':"
                f"x=(w-text_w)/2:y={y_pos}:"
                f"fontsize=56:fontcolor={color}:"
                f"borderw=4:bordercolor=black:"
                f"enable='between(t,{t:.2f},{t+dur:.2f})'"
            )
        t += dur

    text_filters.append(
        "drawtext=text='THE AI DOLLAR':"
        "x=(w-text_w)/2:y=80:fontsize=38:fontcolor=0xFFD700:"
        "borderw=3:bordercolor=black"
    )
    text_filters.append(
        "drawtext=text='@theaidollar1741':"
        "x=(w-text_w)/2:y=h-100:fontsize=28:fontcolor=0xFFD700:"
        "borderw=2:bordercolor=black"
    )

    full_filter = ";".join(filter_parts) + ";[slideshow]" + ",".join(text_filters) + "[outv]"

    audio_input_idx = num_inputs
    cmd = [
        FFMPEG, '-y',
        *input_args,
        '-i', audio_file,
        '-filter_complex', full_filter,
        '-map', '[outv]', '-map', f'{audio_input_idx}:a',
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        output_file
    ]

    print(f"🔧 Running FFmpeg ({len(slides)} slides with images)...")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(timeout=240)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        print("❌ FFmpeg timed out")
        return False

    if proc.returncode != 0:
        err = stderr.decode('utf-8', errors='replace')[-800:]
        print(f"❌ FFmpeg image mode failed: {err}")
        print("⚠️ Retrying with simple mode...")
        return create_video_simple(slides, audio_file, output_file)

    print("✅ Video created with images!")
    return True


def create_video_simple(slides, audio_file, output_file):
    audio_duration = get_audio_duration(audio_file)
    total_slide_dur = sum(s['duration'] for s in slides)
    scale = audio_duration / total_slide_dur if total_slide_dur > 0 else 1.0

    filters = []
    filters.append(
        "drawtext=text='THE AI DOLLAR':"
        "x=(w-text_w)/2:y=80:fontsize=38:fontcolor=0xFFD700:"
        "borderw=3:bordercolor=black"
    )

    t = 0
    for slide in slides:
        dur = slide['duration'] * scale
        lines = slide['text'].split('\n')
        num_lines = len(lines)
        start_y = f"(h/2)-{(num_lines * 35)}"

        for li, line in enumerate(lines):
            escaped = escape_ffmpeg_text(line)
            y_pos = f"({start_y})+{li * 70}"
            color = "white" if li == 0 else "0x00DDFF"
            filters.append(
                f"drawtext=text='{escaped}':"
                f"x=(w-text_w)/2:y={y_pos}:"
                f"fontsize=56:fontcolor={color}:"
                f"borderw=4:bordercolor=black:"
                f"enable='between(t,{t:.2f},{t+dur:.2f})'"
            )
        t += dur

    filters.append(
        "drawtext=text='@theaidollar1741':"
        "x=(w-text_w)/2:y=h-100:fontsize=28:fontcolor=0xFFD700:"
        "borderw=2:bordercolor=black"
    )

    vf = ",".join(filters)
    cmd = [
        FFMPEG, '-y',
        '-f', 'lavfi', '-i', 'color=c=0x0A0A2E:size=1080x1920:rate=30',
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
        print(f"❌ FFmpeg failed (code {proc.returncode})")
        print(stderr.decode('utf-8', errors='replace')[-500:])
        return False

    print("✅ Video created (simple mode)")
    return True


def generate_daily_video():
    day_number = int(datetime.now().strftime("%j"))
    hour = int(datetime.now().strftime("%H"))
    index = (day_number * 3 + hour) % len(CONTENT_TOPICS)
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

        print("🎬 Creating video...")
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
