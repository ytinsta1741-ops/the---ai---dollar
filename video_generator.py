#!/usr/bin/env python3
"""
The AI Dollar - Video Generator
Creates videos using FFmpeg (no Pillow needed) + gTTS voiceover
"""

import os
import subprocess
from datetime import datetime

# Get bundled FFmpeg binary
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
        "title": "ChatGPT Side Hustle Making $500/Week",
        "hook": "Wait, people are actually making 500 dollars per week with ChatGPT?",
        "script": "ChatGPT has created a new income opportunity. Businesses need content, and ChatGPT helps you generate it fast. Start by offering AI-powered content creation services. Charge 200 to 500 dollars per project. With just 2 clients per week, you hit 500 dollars or more.",
        "cta": "Subscribe to The AI Dollar for daily AI money tips!",
        "keywords": ["ChatGPT", "Money", "Side Hustle"],
    },
    {
        "title": "5 AI Tools Making People Rich Right Now",
        "hook": "These 5 AI tools are making people passive income right now.",
        "script": "Tool one: Midjourney, generate art for 100 dollars per commission. Tool two: ChatGPT, sell content creation services. Tool three: Claude, AI copywriting. Tool four: Runway, video creation. Tool five: Dify, build AI apps with no code. Start with one tool and scale.",
        "cta": "Follow The AI Dollar for more AI money strategies!",
        "keywords": ["AI Tools", "Money", "Passive Income"],
    },
    {
        "title": "This AI Made Me $1000 In 24 Hours",
        "hook": "One AI tool did something unexpected and made me 1000 dollars in 24 hours.",
        "script": "I tested an AI tool for 24 hours straight. I used it to create digital products and sell on Gumroad. Got 15 sales at 67 dollars each. Total was over 1000 dollars. The combo? ChatGPT plus Midjourney. Write with ChatGPT, illustrate with Midjourney, sell on Gumroad.",
        "cta": "Like and subscribe for more real AI income strategies!",
        "keywords": ["AI Money", "Digital Products", "Quick Cash"],
    },
    {
        "title": "Best Free AI Tools To Make Money in 2026",
        "hook": "Most people have no idea these free AI tools can make them money.",
        "script": "Free AI tools that work: ChatGPT free tier for content creation. Midjourney free trial for art. Claude free for copywriting. Pika for video creation. Dify for no-code AI apps. Combine any two of these and you have a real money-making business starting today.",
        "cta": "Subscribe to The AI Dollar and never miss a money tip!",
        "keywords": ["Free Tools", "AI", "Money"],
    }
]


def create_audio(text, output_path):
    """Generate TTS audio using gTTS"""
    from gtts import gTTS
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(output_path)


def escape_ffmpeg_text(text):
    """Escape special characters for FFmpeg drawtext filter"""
    return text.replace("'", "\\'").replace(":", "\\:").replace("$", "\\$").replace("%", "%%")


def create_video_ffmpeg(title, script_lines, audio_file, output_file, duration=30):
    """Create branded video using FFmpeg drawtext — no Pillow needed"""

    t = escape_ffmpeg_text(title)
    line1 = escape_ffmpeg_text(script_lines[0][:50] if len(script_lines) > 0 else "")
    line2 = escape_ffmpeg_text(script_lines[1][:50] if len(script_lines) > 1 else "")
    line3 = escape_ffmpeg_text(script_lines[2][:50] if len(script_lines) > 2 else "")
    line4 = escape_ffmpeg_text(script_lines[3][:50] if len(script_lines) > 3 else "")

    vf = (
        # Dark blue gradient background
        "color=c=0x0A0A28:size=1080x1920:duration={dur},"
        # Channel name
        "drawtext=text='THE AI DOLLAR':x=(w-text_w)/2:y=160:fontsize=72:fontcolor=0xFFD700:box=0,"
        # Gold line separator
        "drawtext=text='━━━━━━━━━━━━━━━━━━━━━━━━━':x=(w-text_w)/2:y=270:fontsize=40:fontcolor=0xFFD700,"
        # Title
        "drawtext=text='{title}':x=(w-text_w)/2:y=380:fontsize=50:fontcolor=white:box=1:boxcolor=0x00000080:boxborderw=10,"
        # Script lines
        "drawtext=text='{l1}':x=(w-text_w)/2:y=600:fontsize=38:fontcolor=0xDDDDEE,"
        "drawtext=text='{l2}':x=(w-text_w)/2:y=660:fontsize=38:fontcolor=0xDDDDEE,"
        "drawtext=text='{l3}':x=(w-text_w)/2:y=720:fontsize=38:fontcolor=0xDDDDEE,"
        "drawtext=text='{l4}':x=(w-text_w)/2:y=780:fontsize=38:fontcolor=0xDDDDEE,"
        # Bottom branding
        "drawtext=text='━━━━━━━━━━━━━━━━━━━━━━━━━':x=(w-text_w)/2:y=1650:fontsize=40:fontcolor=0xFFD700,"
        "drawtext=text='@theaidollar1741':x=(w-text_w)/2:y=1720:fontsize=58:fontcolor=0xFFD700,"
        "drawtext=text='Finance + AI = Your Future':x=(w-text_w)/2:y=1810:fontsize=40:fontcolor=0xAAAAAA"
    ).format(dur=duration, title=t, l1=line1, l2=line2, l3=line3, l4=line4)

    cmd = [
        FFMPEG, '-y',
        '-f', 'lavfi', '-i', f'color=c=0x0A0A28:size=1080x1920:duration={duration}',
        '-i', audio_file,
        '-vf', vf,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        output_file
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        print(f"❌ FFmpeg stderr:\n{proc.stderr[-800:]}")
        return False
    return True


def generate_daily_video():
    """Generate a real video with TTS audio and text overlay"""
    day_number = int(datetime.now().strftime("%j"))
    topic = CONTENT_TOPICS[day_number % len(CONTENT_TOPICS)]

    os.makedirs(CONFIG['output_dir'], exist_ok=True)

    output_file = f"{CONFIG['output_dir']}/the_ai_dollar_{day_number}.mp4"
    audio_file  = f"{CONFIG['output_dir']}/audio_{day_number}.mp3"

    try:
        # 1. Generate voiceover
        print("🎤 Generating voiceover...")
        voiceover = f"{topic['hook']} {topic['script']} {topic['cta']}"
        create_audio(voiceover, audio_file)
        print("✅ Audio ready")

        # 2. Create video with FFmpeg drawtext
        print("🎬 Creating video...")
        script_lines = topic['script'].split(". ")
        ok = create_video_ffmpeg(topic['title'], script_lines, audio_file, output_file)

        if not ok:
            return {"status": "error", "message": "FFmpeg video creation failed"}

        print(f"✅ Video created: {output_file}")

        # Cleanup audio
        try:
            os.remove(audio_file)
        except Exception:
            pass

        return {
            "status": "success",
            "video": output_file,
            "title": topic['title'],
            "script": voiceover,
            "keywords": topic['keywords']
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
