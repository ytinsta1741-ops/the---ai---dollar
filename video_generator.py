#!/usr/bin/env python3
"""
The AI Dollar - Video Generator
Creates real videos with TTS voiceover + animated text frame
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path

# Get FFmpeg binary from imageio_ffmpeg (bundled, no system install needed)
try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"✅ FFmpeg found: {FFMPEG}")
except Exception as e:
    FFMPEG = "ffmpeg"
    print(f"⚠️ Using system ffmpeg: {e}")

CONFIG = {
    "output_dir": "./videos",
    "pexels_api_key": os.getenv("PEXELS_API_KEY", "563492ad6f91700001000001"),
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
        "title": "5 AI Tools Making People Money Right Now",
        "hook": "These 5 AI tools are making people passive income right now.",
        "script": "Tool 1: Midjourney, generate art for 100 dollars per commission. Tool 2: ChatGPT, sell content creation services. Tool 3: Claude, AI copywriting. Tool 4: Runway, video creation. Tool 5: Dify, build AI apps with no code. Start with one tool and scale from there.",
        "cta": "Follow The AI Dollar for more AI money strategies!",
        "keywords": ["AI Tools", "Money", "Passive Income"],
    },
    {
        "title": "This AI Made Me $1000 In 24 Hours",
        "hook": "One AI tool did something unexpected and made me 1000 dollars in 24 hours.",
        "script": "I tested an AI tool for 24 hours straight. I used it to create digital products and sell on Gumroad. Got 15 sales at 67 dollars each. Total was over 1000 dollars. The tool combo? ChatGPT plus Midjourney. Write with ChatGPT, illustrate with Midjourney, sell on Gumroad. Simple.",
        "cta": "Like and subscribe for more real AI income strategies!",
        "keywords": ["AI Money", "Digital Products", "Quick Cash"],
    },
    {
        "title": "Best Free AI Tools To Make Money in 2026",
        "hook": "Most people have no idea these free AI tools can make them money.",
        "script": "Free AI tools that actually work: ChatGPT free tier for content creation. Midjourney free trial for art. Claude free for copywriting. Pika for video creation. Dify for building no-code AI apps. Combine any two of these and you have a real money-making business starting today.",
        "cta": "Subscribe to The AI Dollar and never miss a money tip!",
        "keywords": ["Free Tools", "AI", "Money"],
    }
]


def create_audio(text, output_path):
    """Generate TTS audio using gTTS"""
    from gtts import gTTS
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(output_path)


def create_frame(title, lines, output_path, width=1080, height=1920):
    """Create a branded video frame with PIL"""
    from PIL import Image, ImageDraw

    img = Image.new('RGB', (width, height), color=(8, 8, 20))
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(height):
        r = int(8 + (y / height) * 20)
        g = int(8 + (y / height) * 5)
        b = int(20 + (y / height) * 40)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Try to load a font, fall back to default
    try:
        from PIL import ImageFont
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        font_sml = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
    except Exception:
        from PIL import ImageFont
        font_big = ImageFont.load_default()
        font_med = font_big
        font_sml = font_big

    # Channel branding
    draw.text((width // 2, 180), "THE AI DOLLAR", font=font_big, fill=(255, 200, 0), anchor="mm")
    draw.line([(100, 250), (width - 100, 250)], fill=(255, 200, 0), width=3)

    # Title
    y = 380
    words = title.split()
    current_line = ""
    title_lines = []
    for word in words:
        test = (current_line + " " + word).strip()
        if len(test) > 22:
            title_lines.append(current_line)
            current_line = word
        else:
            current_line = test
    if current_line:
        title_lines.append(current_line)

    for tl in title_lines:
        draw.text((width // 2, y), tl, font=font_med, fill=(255, 255, 255), anchor="mm")
        y += 80

    # Divider
    y += 40
    draw.line([(150, y), (width - 150, y)], fill=(80, 80, 120), width=2)
    y += 60

    # Script lines
    for line in lines[:7]:
        line = line.strip()
        if not line:
            continue
        # Wrap long lines
        words2 = line.split()
        cur = ""
        wrapped = []
        for w in words2:
            t = (cur + " " + w).strip()
            if len(t) > 30:
                wrapped.append(cur)
                cur = w
            else:
                cur = t
        if cur:
            wrapped.append(cur)
        for wl in wrapped:
            draw.text((width // 2, y), wl, font=font_sml, fill=(210, 210, 220), anchor="mm")
            y += 56
        y += 10

    # Bottom
    draw.line([(100, height - 280), (width - 100, height - 280)], fill=(255, 200, 0), width=3)
    draw.text((width // 2, height - 200), "@theaidollar1741", font=font_med, fill=(255, 200, 0), anchor="mm")
    draw.text((width // 2, height - 110), "Finance + AI = Your Future", font=font_sml, fill=(160, 160, 180), anchor="mm")

    img.save(output_path)


def generate_daily_video():
    """Generate a real video with TTS audio and branded frame"""
    day_number = int(datetime.now().strftime("%j"))
    topic = CONTENT_TOPICS[day_number % len(CONTENT_TOPICS)]

    os.makedirs(CONFIG['output_dir'], exist_ok=True)

    output_file = f"{CONFIG['output_dir']}/the_ai_dollar_{day_number}.mp4"
    audio_file  = f"{CONFIG['output_dir']}/audio_{day_number}.mp3"
    frame_file  = f"{CONFIG['output_dir']}/frame_{day_number}.png"

    try:
        # 1. Generate voiceover audio
        print("🎤 Generating voiceover...")
        voiceover = f"{topic['hook']} {topic['script']} {topic['cta']}"
        create_audio(voiceover, audio_file)
        print("✅ Audio ready")

        # 2. Create video frame
        print("🎨 Creating video frame...")
        script_lines = topic['script'].split(". ")
        create_frame(topic['title'], script_lines, frame_file)
        print("✅ Frame ready")

        # 3. Combine into video with FFmpeg
        print("🎬 Encoding video...")
        cmd = [
            FFMPEG, '-y',
            '-loop', '1', '-i', frame_file,
            '-i', audio_file,
            '-c:v', 'libx264',
            '-tune', 'stillimage',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            output_file
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if proc.returncode != 0:
            print(f"❌ FFmpeg error:\n{proc.stderr[-500:]}")
            return {"status": "error", "message": "ffmpeg failed"}

        print(f"✅ Video created: {output_file}")

        # Cleanup temp files
        for f in [audio_file, frame_file]:
            try:
                os.remove(f)
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
        print(f"❌ Video generation error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
