#!/usr/bin/env python3
"""
The AI Dollar - Video Generator
Creates YouTube Shorts style videos with timed text + TTS voiceover
"""

import os
import subprocess
import json
from datetime import datetime

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"✅ FFmpeg ready: {FFMPEG}")
except Exception as e:
    FFMPEG = "ffmpeg"
    print(f"⚠️ Using system ffmpeg: {e}")

CONFIG = {
    "output_dir": "./videos",
}

CONTENT_TOPICS = [
    {
        "title": "What is AI?",
        "slides": [
            {"text": "What is AI?", "duration": 3},
            {"text": "AI stands for\\nArtificial Intelligence", "duration": 3},
            {"text": "It lets machines\\nlearn from data", "duration": 3},
            {"text": "And make decisions\\nlike humans do", "duration": 3},
            {"text": "ChatGPT, Siri, Tesla\\nall use AI", "duration": 3},
            {"text": "AI is changing\\nEVERYTHING", "duration": 3},
            {"text": "Follow for more\\nAI insights", "duration": 3},
        ],
        "voiceover": "What is AI? AI stands for Artificial Intelligence. It lets machines learn from data and make decisions like humans do. ChatGPT, Siri, and Tesla all use AI every day. AI is changing everything around us. Follow The AI Dollar for more AI insights.",
        "keywords": ["AI", "Artificial Intelligence", "Tech"],
    },
    {
        "title": "Make $500/Week with ChatGPT",
        "slides": [
            {"text": "Make $500 per week\\nwith ChatGPT", "duration": 3},
            {"text": "Step 1\\nLearn prompt engineering", "duration": 3},
            {"text": "Step 2\\nOffer content writing", "duration": 3},
            {"text": "Step 3\\nCharge $200 per project", "duration": 3},
            {"text": "Just 2-3 clients\\n= $500+ weekly", "duration": 3},
            {"text": "Start TODAY\\nnot tomorrow", "duration": 3},
            {"text": "Follow for more\\nAI money tips", "duration": 3},
        ],
        "voiceover": "You can make 500 dollars per week with ChatGPT. Step one, learn prompt engineering. Step two, offer content writing services to businesses. Step three, charge 200 dollars per project. With just 2 to 3 clients, that's 500 dollars or more every single week. Start today, not tomorrow. Follow The AI Dollar for more AI money tips.",
        "keywords": ["ChatGPT", "Money", "Side Hustle"],
    },
    {
        "title": "5 AI Tools Making People Rich",
        "slides": [
            {"text": "5 AI Tools Making\\nPeople RICH", "duration": 3},
            {"text": "1. ChatGPT\\nContent creation", "duration": 3},
            {"text": "2. Midjourney\\nAI art for $100+", "duration": 3},
            {"text": "3. Claude\\nAI copywriting", "duration": 3},
            {"text": "4. Runway\\nVideo creation", "duration": 3},
            {"text": "5. Dify\\nNo-code AI apps", "duration": 2.5},
            {"text": "Pick ONE and\\nstart earning", "duration": 2.5},
            {"text": "Subscribe for more!", "duration": 2},
        ],
        "voiceover": "5 AI tools making people rich right now. Number one, ChatGPT for content creation. Number two, Midjourney for AI art commissions at 100 dollars each. Number three, Claude for AI copywriting. Number four, Runway for video creation. Number five, Dify for building no-code AI apps. Pick one tool and start earning today. Subscribe for more.",
        "keywords": ["AI Tools", "Money", "Passive Income"],
    },
    {
        "title": "AI Made Me $1000 in 24 Hours",
        "slides": [
            {"text": "AI made me $1000\\nin 24 hours", "duration": 3},
            {"text": "I used ChatGPT +\\nMidjourney", "duration": 3},
            {"text": "Created digital\\nproducts", "duration": 3},
            {"text": "Sold them on\\nGumroad", "duration": 3},
            {"text": "15 sales at $67\\neach", "duration": 3},
            {"text": "Total = $1,005", "duration": 3},
            {"text": "You can do this\\nTODAY", "duration": 2.5},
            {"text": "Follow @theaidollar1741", "duration": 2},
        ],
        "voiceover": "AI made me 1000 dollars in just 24 hours. I used ChatGPT and Midjourney together. I created digital products and sold them on Gumroad. I got 15 sales at 67 dollars each. That's a total of 1005 dollars in one day. You can do this today. Follow The AI Dollar for more.",
        "keywords": ["AI Money", "Digital Products", "Quick Cash"],
    },
    {
        "title": "Best FREE AI Tools 2026",
        "slides": [
            {"text": "Best FREE AI Tools\\nin 2026", "duration": 3},
            {"text": "ChatGPT Free\\nContent creation", "duration": 3},
            {"text": "Claude Free\\nCopywriting", "duration": 3},
            {"text": "Pika Free\\nVideo creation", "duration": 3},
            {"text": "Canva AI\\nDesign anything", "duration": 3},
            {"text": "Combine any TWO\\n= real business", "duration": 3},
            {"text": "Subscribe for\\ndaily AI tips!", "duration": 3},
        ],
        "voiceover": "Here are the best free AI tools in 2026. ChatGPT free tier for content creation. Claude free for copywriting. Pika for free video creation. Canva AI for designing anything. Combine any two of these and you have a real money-making business starting today. Subscribe to The AI Dollar for daily AI tips.",
        "keywords": ["Free Tools", "AI", "Money"],
    },
    {
        "title": "How AI Will Replace 90% of Jobs",
        "slides": [
            {"text": "AI will replace\\n90%% of jobs", "duration": 3},
            {"text": "Customer service?\\nAI chatbots", "duration": 3},
            {"text": "Data entry?\\nAlready automated", "duration": 3},
            {"text": "Writing?\\nChatGPT does it", "duration": 3},
            {"text": "But here is\\nthe good news", "duration": 3},
            {"text": "AI creates NEW\\njobs too", "duration": 3},
            {"text": "Learn AI now\\nor get left behind", "duration": 3},
        ],
        "voiceover": "AI will replace 90 percent of jobs. Customer service? AI chatbots handle it. Data entry? Already automated. Writing? ChatGPT does it faster. But here is the good news. AI creates new jobs too. The question is, will you learn AI now, or get left behind? Follow The AI Dollar.",
        "keywords": ["AI Jobs", "Future", "Automation"],
    },
]


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


def create_video_ffmpeg(slides, audio_file, output_file):
    audio_duration = get_audio_duration(audio_file)

    total_slide_duration = sum(s['duration'] for s in slides)
    scale = audio_duration / total_slide_duration if total_slide_duration > 0 else 1.0

    filters = []

    filters.append(
        "drawtext=text='THE AI DOLLAR':"
        "x=(w-text_w)/2:y=80:fontsize=36:fontcolor=0xFFD700:"
        "borderw=2:bordercolor=0x000000"
    )

    t = 0
    for slide in slides:
        dur = slide['duration'] * scale
        lines = slide['text'].split('\\n')

        if len(lines) == 1:
            escaped = escape_ffmpeg_text(lines[0])
            filters.append(
                f"drawtext=text='{escaped}':"
                f"x=(w-text_w)/2:y=(h-text_h)/2:"
                f"fontsize=52:fontcolor=white:"
                f"borderw=3:bordercolor=0x000000:"
                f"enable='between(t,{t:.2f},{t+dur:.2f})'"
            )
        else:
            escaped1 = escape_ffmpeg_text(lines[0])
            escaped2 = escape_ffmpeg_text(lines[1]) if len(lines) > 1 else ""
            filters.append(
                f"drawtext=text='{escaped1}':"
                f"x=(w-text_w)/2:y=(h/2)-50:"
                f"fontsize=52:fontcolor=white:"
                f"borderw=3:bordercolor=0x000000:"
                f"enable='between(t,{t:.2f},{t+dur:.2f})'"
            )
            if escaped2:
                filters.append(
                    f"drawtext=text='{escaped2}':"
                    f"x=(w-text_w)/2:y=(h/2)+20:"
                    f"fontsize=52:fontcolor=0x00DDFF:"
                    f"borderw=3:bordercolor=0x000000:"
                    f"enable='between(t,{t:.2f},{t+dur:.2f})'"
                )
        t += dur

    filters.append(
        "drawtext=text='@theaidollar1741':"
        "x=(w-text_w)/2:y=h-120:fontsize=32:fontcolor=0xFFD700:"
        "borderw=2:bordercolor=0x000000"
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

    print(f"🔧 Running FFmpeg ({len(slides)} slides)...")
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

    print("✅ FFmpeg done")
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

    try:
        print("🎤 Generating voiceover...")
        create_audio(topic['voiceover'], audio_file)
        print("✅ Audio ready")

        print("🎬 Creating video...")
        ok = create_video_ffmpeg(topic['slides'], audio_file, output_file)

        if not ok:
            return {"status": "error", "message": "FFmpeg video creation failed"}

        print(f"✅ Video created: {output_file}")

        try:
            os.remove(audio_file)
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
