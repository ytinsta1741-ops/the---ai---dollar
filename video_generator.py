#!/usr/bin/env python3
"""
The AI Dollar - Video Generator
YouTube Shorts style: stock images + text overlay + TTS voiceover
"""

import os
import subprocess
import requests
from datetime import datetime

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"✅ FFmpeg ready: {FFMPEG}")
except Exception as e:
    FFMPEG = "ffmpeg"
    print(f"⚠️ Using system ffmpeg: {e}")

CONFIG = {"output_dir": "./videos", "img_dir": "./videos/imgs"}

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

CONTENT_TOPICS = [
    {
        "title": "What is AI?",
        "search_queries": ["artificial intelligence", "robot technology", "computer brain", "futuristic technology", "AI robot", "neural network", "machine learning"],
        "slides": [
            {"text": "What is AI?", "duration": 3},
            {"text": "AI stands for\nArtificial Intelligence", "duration": 3},
            {"text": "It lets machines\nlearn from data", "duration": 3},
            {"text": "And make decisions\nlike humans do", "duration": 3},
            {"text": "ChatGPT, Siri, Tesla\nall use AI", "duration": 3},
            {"text": "AI is changing\nEVERYTHING", "duration": 3},
            {"text": "Follow for more\nAI insights", "duration": 3},
        ],
        "voiceover": "What is AI? AI stands for Artificial Intelligence. It lets machines learn from data and make decisions like humans do. ChatGPT, Siri, and Tesla all use AI every day. AI is changing everything around us. Follow The AI Dollar for more AI insights.",
        "keywords": ["AI", "Artificial Intelligence", "Tech"],
    },
    {
        "title": "Make $500/Week with ChatGPT",
        "search_queries": ["laptop money", "freelancer working", "typing laptop", "online business", "dollar bills", "work from home", "digital entrepreneur"],
        "slides": [
            {"text": "Make $500 per week\nwith ChatGPT", "duration": 3},
            {"text": "Step 1\nLearn prompt engineering", "duration": 3},
            {"text": "Step 2\nOffer content writing", "duration": 3},
            {"text": "Step 3\nCharge $200 per project", "duration": 3},
            {"text": "Just 2-3 clients\n= $500+ weekly", "duration": 3},
            {"text": "Start TODAY\nnot tomorrow", "duration": 3},
            {"text": "Follow for more\nAI money tips", "duration": 3},
        ],
        "voiceover": "You can make 500 dollars per week with ChatGPT. Step one, learn prompt engineering. Step two, offer content writing services to businesses. Step three, charge 200 dollars per project. With just 2 to 3 clients, that's 500 dollars or more every single week. Start today, not tomorrow. Follow The AI Dollar for more AI money tips.",
        "keywords": ["ChatGPT", "Money", "Side Hustle"],
    },
    {
        "title": "5 AI Tools Making People Rich",
        "search_queries": ["AI technology", "digital tools", "money technology", "creative software", "app development", "rich lifestyle", "tech startup", "coding screen"],
        "slides": [
            {"text": "5 AI Tools Making\nPeople RICH", "duration": 3},
            {"text": "1. ChatGPT\nContent creation", "duration": 3},
            {"text": "2. Midjourney\nAI art for $100+", "duration": 3},
            {"text": "3. Claude\nAI copywriting", "duration": 3},
            {"text": "4. Runway\nVideo creation", "duration": 3},
            {"text": "5. Dify\nNo-code AI apps", "duration": 2.5},
            {"text": "Pick ONE and\nstart earning", "duration": 2.5},
            {"text": "Subscribe for more!", "duration": 2},
        ],
        "voiceover": "5 AI tools making people rich right now. Number one, ChatGPT for content creation. Number two, Midjourney for AI art commissions at 100 dollars each. Number three, Claude for AI copywriting. Number four, Runway for video creation. Number five, Dify for building no-code AI apps. Pick one tool and start earning today. Subscribe for more.",
        "keywords": ["AI Tools", "Money", "Passive Income"],
    },
    {
        "title": "AI Made Me $1000 in 24 Hours",
        "search_queries": ["money cash", "online earnings", "laptop success", "digital product", "ecommerce", "gumroad sales", "passive income"],
        "slides": [
            {"text": "AI made me $1000\nin 24 hours", "duration": 3},
            {"text": "I used ChatGPT +\nMidjourney", "duration": 3},
            {"text": "Created digital\nproducts", "duration": 3},
            {"text": "Sold them on\nGumroad", "duration": 3},
            {"text": "15 sales at $67\neach", "duration": 3},
            {"text": "Total = $1,005", "duration": 3},
            {"text": "You can do this\nTODAY", "duration": 2.5},
            {"text": "Follow @theaidollar1741", "duration": 2},
        ],
        "voiceover": "AI made me 1000 dollars in just 24 hours. I used ChatGPT and Midjourney together. I created digital products and sold them on Gumroad. I got 15 sales at 67 dollars each. That's a total of 1005 dollars in one day. You can do this today. Follow The AI Dollar for more.",
        "keywords": ["AI Money", "Digital Products", "Quick Cash"],
    },
    {
        "title": "Best FREE AI Tools 2026",
        "search_queries": ["free software", "AI application", "smartphone apps", "creative tools", "design software", "video editing", "writing tools"],
        "slides": [
            {"text": "Best FREE AI Tools\nin 2026", "duration": 3},
            {"text": "ChatGPT Free\nContent creation", "duration": 3},
            {"text": "Claude Free\nCopywriting", "duration": 3},
            {"text": "Pika Free\nVideo creation", "duration": 3},
            {"text": "Canva AI\nDesign anything", "duration": 3},
            {"text": "Combine any TWO\n= real business", "duration": 3},
            {"text": "Subscribe for\ndaily AI tips!", "duration": 3},
        ],
        "voiceover": "Here are the best free AI tools in 2026. ChatGPT free tier for content creation. Claude free for copywriting. Pika for free video creation. Canva AI for designing anything. Combine any two of these and you have a real money-making business starting today. Subscribe to The AI Dollar for daily AI tips.",
        "keywords": ["Free Tools", "AI", "Money"],
    },
    {
        "title": "How AI Will Replace 90% of Jobs",
        "search_queries": ["office workers", "automation factory", "robot working", "unemployment", "future jobs", "AI workplace", "technology office"],
        "slides": [
            {"text": "AI will replace\n90%% of jobs", "duration": 3},
            {"text": "Customer service?\nAI chatbots", "duration": 3},
            {"text": "Data entry?\nAlready automated", "duration": 3},
            {"text": "Writing?\nChatGPT does it", "duration": 3},
            {"text": "But here is\nthe good news", "duration": 3},
            {"text": "AI creates NEW\njobs too", "duration": 3},
            {"text": "Learn AI now\nor get left behind", "duration": 3},
        ],
        "voiceover": "AI will replace 90 percent of jobs. Customer service? AI chatbots handle it. Data entry? Already automated. Writing? ChatGPT does it faster. But here is the good news. AI creates new jobs too. The question is, will you learn AI now, or get left behind? Follow The AI Dollar.",
        "keywords": ["AI Jobs", "Future", "Automation"],
    },
]


def fetch_pexels_images(queries, num_images, save_dir):
    """Download portrait images from Pexels for each slide"""
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
                    img_url = photo["src"]["large2x"]
                    img_resp = requests.get(img_url, timeout=15)
                    if img_resp.status_code == 200:
                        with open(img_path, 'wb') as f:
                            f.write(img_resp.content)
                        images.append(img_path)
                        print(f"  📸 Image {i+1}: {query}")
                        continue

            print(f"  ⚠️ No image for '{query}', using color bg")
            images.append(None)

        except Exception as e:
            print(f"  ⚠️ Image fetch error: {e}")
            images.append(None)

    return images


def create_audio(text, output_path):
    from gtts import gTTS
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(output_path)


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
    return 21


def escape_ffmpeg_text(text):
    return text.replace("'", "\\'").replace(":", "\\:").replace("$", "\\$").replace("%", "%%")


def create_video_ffmpeg(slides, images, audio_file, output_file):
    audio_duration = get_audio_duration(audio_file)
    total_slide_dur = sum(s['duration'] for s in slides)
    scale = audio_duration / total_slide_dur if total_slide_dur > 0 else 1.0

    valid_images = [img for img in images if img is not None]

    if not valid_images:
        input_args = ['-f', 'lavfi', '-i', 'color=c=0x0A0A2E:size=1080x1920:rate=30']
        base_label = "[0:v]"
    else:
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
                f"[{seg_label}]drawbox=x=0:y=0:w=1080:h=1920:color=black@0.55:t=fill[{dark_label}]"
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

            if len(lines) == 1:
                escaped = escape_ffmpeg_text(lines[0])
                text_filters.append(
                    f"drawtext=text='{escaped}':"
                    f"x=(w-text_w)/2:y=(h-text_h)/2:"
                    f"fontsize=58:fontcolor=white:"
                    f"borderw=4:bordercolor=black:"
                    f"enable='between(t,{t:.2f},{t+dur:.2f})'"
                )
            else:
                escaped1 = escape_ffmpeg_text(lines[0])
                text_filters.append(
                    f"drawtext=text='{escaped1}':"
                    f"x=(w-text_w)/2:y=(h/2)-60:"
                    f"fontsize=58:fontcolor=white:"
                    f"borderw=4:bordercolor=black:"
                    f"enable='between(t,{t:.2f},{t+dur:.2f})'"
                )
                if len(lines) > 1:
                    escaped2 = escape_ffmpeg_text(lines[1])
                    text_filters.append(
                        f"drawtext=text='{escaped2}':"
                        f"x=(w-text_w)/2:y=(h/2)+20:"
                        f"fontsize=58:fontcolor=0x00DDFF:"
                        f"borderw=4:bordercolor=black:"
                        f"enable='between(t,{t:.2f},{t+dur:.2f})'"
                    )
            t += dur

        text_filters.append(
            "drawtext=text='THE AI DOLLAR':"
            "x=(w-text_w)/2:y=80:fontsize=40:fontcolor=0xFFD700:"
            "borderw=3:bordercolor=black"
        )
        text_filters.append(
            "drawtext=text='@theaidollar1741':"
            "x=(w-text_w)/2:y=h-100:fontsize=30:fontcolor=0xFFD700:"
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
            stdout, stderr = proc.communicate(timeout=180)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            print("❌ FFmpeg timed out")
            return False

        if proc.returncode != 0:
            err = stderr.decode('utf-8', errors='replace')[-800:]
            print(f"❌ FFmpeg failed (code {proc.returncode})")
            print(err)
            print("⚠️ Retrying with simple mode...")
            return create_video_simple(slides, audio_file, output_file)

        print("✅ FFmpeg done - video with images!")
        return True

    return create_video_simple(slides, audio_file, output_file)


def create_video_simple(slides, audio_file, output_file):
    """Fallback: text-only video if image mode fails"""
    audio_duration = get_audio_duration(audio_file)
    total_slide_dur = sum(s['duration'] for s in slides)
    scale = audio_duration / total_slide_dur if total_slide_dur > 0 else 1.0

    filters = []
    filters.append(
        "drawtext=text='THE AI DOLLAR':"
        "x=(w-text_w)/2:y=80:fontsize=40:fontcolor=0xFFD700:"
        "borderw=3:bordercolor=black"
    )

    t = 0
    for slide in slides:
        dur = slide['duration'] * scale
        lines = slide['text'].split('\n')
        if len(lines) == 1:
            escaped = escape_ffmpeg_text(lines[0])
            filters.append(
                f"drawtext=text='{escaped}':"
                f"x=(w-text_w)/2:y=(h-text_h)/2:"
                f"fontsize=58:fontcolor=white:"
                f"borderw=4:bordercolor=black:"
                f"enable='between(t,{t:.2f},{t+dur:.2f})'"
            )
        else:
            escaped1 = escape_ffmpeg_text(lines[0])
            filters.append(
                f"drawtext=text='{escaped1}':"
                f"x=(w-text_w)/2:y=(h/2)-60:"
                f"fontsize=58:fontcolor=white:"
                f"borderw=4:bordercolor=black:"
                f"enable='between(t,{t:.2f},{t+dur:.2f})'"
            )
            if len(lines) > 1:
                escaped2 = escape_ffmpeg_text(lines[1])
                filters.append(
                    f"drawtext=text='{escaped2}':"
                    f"x=(w-text_w)/2:y=(h/2)+20:"
                    f"fontsize=58:fontcolor=0x00DDFF:"
                    f"borderw=4:bordercolor=black:"
                    f"enable='between(t,{t:.2f},{t+dur:.2f})'"
                )
        t += dur

    filters.append(
        "drawtext=text='@theaidollar1741':"
        "x=(w-text_w)/2:y=h-100:fontsize=30:fontcolor=0xFFD700:"
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
        stdout, stderr = proc.communicate(timeout=180)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        print("❌ FFmpeg timed out")
        return False

    if proc.returncode != 0:
        print(f"❌ FFmpeg failed (code {proc.returncode})")
        print(stderr.decode('utf-8', errors='replace')[-500:])
        return False

    print("✅ FFmpeg done (simple mode)")
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
        print("✅ Audio ready")

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
