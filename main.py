#!/usr/bin/env python3
"""
The AI Dollar - Complete Automation
Generates videos, uploads to YouTube, posts to Instagram
Runs on schedule: 6 slots optimized for US peak hours
"""

import os
import sys
import time
import random
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import schedule
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from video_generator import generate_daily_video, generate_long_video
from instagram_poster import post_to_instagram


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path

        if path == "/test-instagram":
            print("\n[TEST] Manual Instagram test triggered!")
            try:
                result = generate_daily_video()
                if result['status'] == 'success':
                    video_path = result['video']
                    title = result['title']
                    keywords = result.get('keywords', [])
                    success = upload_to_instagram(video_path, title, keywords=keywords)
                    msg = b"[OK] Instagram test posted!" if success else b"[ERR] Instagram test failed"
                else:
                    msg = b"[ERR] Video generation failed"
            except Exception as e:
                msg = f"[ERR] {str(e)}".encode()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(msg)
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"The AI Dollar is running!")

    def log_message(self, format, *args):
        pass


def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"[OK] Health server running on port {port}")
    server.serve_forever()


def upload_to_youtube(video_path, title, description, is_short=True, keywords=None, thumbnail_path=None):
    """Upload video to YouTube using OAuth refresh token"""
    try:
        refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN", "")
        if not refresh_token:
            print("[WARN] YOUTUBE_REFRESH_TOKEN not set -- skipping YouTube")
            return False

        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError

        CLIENT_ID     = os.getenv("YOUTUBE_CLIENT_ID", "")
        CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
        if not CLIENT_ID or not CLIENT_SECRET:
            print("[WARN] YOUTUBE_CLIENT_ID or YOUTUBE_CLIENT_SECRET not set -- skipping YouTube")
            return False

        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scopes=["https://www.googleapis.com/auth/youtube.upload"]
        )

        youtube = build("youtube", "v3", credentials=creds)

        topic_tags = keywords if keywords else []
        base_tags = [
            "personal finance", "money tips", "investing for beginners",
            "financial literacy", "how to invest", "money management",
            "wealth building", "passive income", "financial education",
            "stock market for beginners", "save money", "make money online",
            "budget tips", "debt free journey", "credit score tips",
            "side hustle ideas 2026", "financial freedom", "money advice",
            "finance tips", "how to get rich", "TheAIDollar",
            "money hacks that work", "rich vs poor habits", "compound interest explained",
            "index funds for beginners", "roth ira explained", "how to save money fast",
            "money mistakes to avoid", "millionaire habits", "financial independence",
            "how to build wealth", "money rules", "investing tips 2026",
        ]
        yt_tags = topic_tags + [t for t in base_tags if t.lower() not in [k.lower() for k in topic_tags]]
        import re
        yt_tags = [re.sub(r'[<>",]', '', t).strip() for t in yt_tags if t.strip()]
        yt_tags = [t[:30] for t in yt_tags if t]
        total = 0
        trimmed = []
        for t in yt_tags:
            added = len(t) + (1 if trimmed else 0)
            if total + added > 450:
                break
            trimmed.append(t)
            total += added
        yt_tags = trimmed

        kw_line = ", ".join(topic_tags[:5]) if topic_tags else "money tips, finance, investing"

        if is_short:
            yt_title = title[:100]
            hooks = [
                "This changes everything about how you think about money.",
                "99% of people don't know this. Now you do.",
                "Watch this before you spend another dollar.",
                "This is the money lesson schools refuse to teach.",
                "If you're broke, this video is your wake-up call.",
                "I wish someone told me this at 18.",
                "This is why most people stay broke forever.",
                "The money truth nobody wants to hear.",
                "Stop what you're doing and watch this.",
                "The financial advice that actually works in 2026.",
                "Most financial gurus won't tell you this for free.",
                "This one money move changed everything for me.",
            ]
            open_loops = [
                "The last tip is the one that changes everything.",
                "Wait for the final part — it's worth 10x the rest.",
                "Tip #3 alone is worth watching the whole video.",
                "The ending will shock you.",
            ]
            yt_desc = (
                f"{kw_line} — {title}\n"
                f"Learn {kw_line} in 60 seconds. Free finance education daily.\n\n"
                f"{random.choice(hooks)}\n"
                f"{random.choice(open_loops)}\n\n"
                f"WATCH MORE:\n"
                f"Subscribe for daily money lessons: https://www.youtube.com/@TheAIDollar?sub_confirmation=1\n\n"
                f"ENGAGE:\n"
                f"Comment your #1 money struggle below\n"
                f"Share this with someone who needs to hear it\n"
                f"Turn on notifications — new videos every day\n\n"
                f"TOPICS COVERED: {kw_line}, personal finance tips, "
                f"how to build wealth, money management for beginners, "
                f"investing basics, financial literacy 2026\n\n"
                f"#Shorts #Finance #Money #Investing #PersonalFinance "
                f"#WealthBuilding #FinancialFreedom #MoneyTips "
                f"#HowToGetRich #PassiveIncome #DebtFree #SideHustle "
                f"#FinancialLiteracy #MakeMoney #MoneyHacks "
                f"#InvestingForBeginners #TheAIDollar "
                f"#MillionaireMindset #FinancialEducation "
                f"#MoneyTok #FinTok #LearnOnYouTube"
            )
            yt_tags.append("Shorts")
        else:
            yt_title = title[:100]
            intros = [
                f"Most people will scroll past this. But if you watch to the end, you'll know more about {kw_line} than 99% of people.",
                f"This is the complete breakdown of {kw_line} that nobody else is giving you for free.",
                f"Everything you need to know about {kw_line} in one video. No fluff. No BS. Just actionable steps.",
                f"I spent hours researching {kw_line} so you don't have to. Here's everything that actually matters.",
                f"This {kw_line} guide is what I wish I had when I started. Watch it twice.",
                f"WARNING: Once you learn this about {kw_line}, you can't unlearn it.",
            ]
            yt_desc = (
                f"{kw_line} — {title} | The AI Dollar\n"
                f"Learn {kw_line}, personal finance tips, and wealth-building strategies. "
                f"Free financial education for beginners and beyond.\n\n"
                f"{random.choice(intros)}\n\n"
                f"TIMESTAMPS:\n"
                f"0:00 - Introduction — why {kw_line} matters\n"
                f"0:45 - The core concept explained simply\n"
                f"2:00 - Real-world examples and proof\n"
                f"4:00 - Step-by-step action plan you can start TODAY\n"
                f"6:00 - Common mistakes that keep people broke\n"
                f"8:00 - The #1 thing to do RIGHT NOW\n\n"
                f"WHAT YOU'LL LEARN:\n"
                f"- How {kw_line} actually works in real life\n"
                f"- The biggest mistakes beginners make\n"
                f"- A step-by-step action plan anyone can follow\n"
                f"- Why starting TODAY beats waiting for 'the right time'\n\n"
                f"FREE RESOURCES:\n"
                f"- High yield savings: Most online banks offer 4-5% APY\n"
                f"- Index fund investing: Fidelity, Vanguard, Schwab (zero minimums)\n"
                f"- Budget tracking: Free apps like Mint or YNAB trial\n\n"
                f"If this helped you, do these 3 things:\n"
                f"1. SUBSCRIBE and turn on ALL notifications\n"
                f"2. COMMENT your biggest takeaway below\n"
                f"3. SHARE with someone who needs to hear this\n\n"
                f"We post 4 videos EVERY DAY — shorts + deep dives.\n"
                f"New here? Start with our most popular videos on the channel page.\n\n"
                f"RELATED TOPICS: {kw_line}, personal finance for beginners, "
                f"how to invest money, budgeting tips, wealth building strategies, "
                f"financial literacy 2026, money management, passive income ideas\n\n"
                f"Subscribe: https://www.youtube.com/@TheAIDollar?sub_confirmation=1\n\n"
                f"#Finance #Money #PersonalFinance #Investing #WealthBuilding "
                f"#FinancialFreedom #MoneyTips #FinancialLiteracy "
                f"#HowToGetRich #StockMarket #PassiveIncome #DebtFree "
                f"#InvestingForBeginners #TheAIDollar "
                f"#MillionaireMindset #FinancialEducation "
                f"#MoneyMindset #WealthSecrets"
            )

        print(f"[TAGS] {len(yt_tags)} tags, {len(','.join(yt_tags))} chars: {yt_tags}")

        def _upload(tags):
            body = {
                "snippet": {
                    "title": yt_title,
                    "description": yt_desc,
                    "tags": tags,
                    "categoryId": "22",
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                },
            }
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"[UPLOAD] YouTube: {int(status.progress() * 100)}% uploaded")
            return response

        try:
            response = _upload(yt_tags)
        except HttpError as e:
            if "invalidTags" in str(e) or "invalid video keywords" in str(e):
                print(f"[WARN] Tags rejected ({e}), retrying with minimal safe tags...")
                safe_tags = ["personal finance", "money tips", "investing", "financial education", "TheAIDollar"]
                try:
                    response = _upload(safe_tags)
                except HttpError as e2:
                    print(f"[WARN] Minimal tags also rejected ({e2}), retrying with no tags...")
                    response = _upload([])
            else:
                raise

        video_id = response.get("id", "")
        print(f"[OK] YouTube uploaded! https://youtube.com/watch?v={video_id}")

        if thumbnail_path and os.path.exists(thumbnail_path) and video_id:
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
                ).execute()
                print(f"[OK] Custom thumbnail set for {video_id}")
            except Exception as te:
                print(f"[WARN] Thumbnail upload failed (requires verified channel): {te}")

        return True

    except Exception as e:
        print(f"[ERR] YouTube error: {e}")
        import traceback
        traceback.print_exc()
        return False


def upload_to_instagram(video_path, title, keywords=None):
    """Upload video to Instagram Reels using instagrapi"""
    username = os.getenv("INSTAGRAM_USERNAME", "")
    password = os.getenv("INSTAGRAM_PASSWORD", "")
    if not username or not password:
        print("[SKIP] Instagram: INSTAGRAM_USERNAME or INSTAGRAM_PASSWORD not set")
        return False

    try:
        from instagrapi import Client

        cl = Client()
        cl.delay_range = [2, 5]

        session_file = "instagram_session.json"
        logged_in = False

        if os.path.exists(session_file):
            try:
                cl.load_settings(session_file)
                cl.login(username, password)
                logged_in = True
                print("[OK] Instagram: resumed session")
            except Exception:
                cl = Client()
                cl.delay_range = [2, 5]

        if not logged_in:
            cl.login(username, password)
            print("[OK] Instagram: fresh login")

        kw_tags = " ".join(f"#{k.replace(' ', '')}" for k in (keywords or [])[:5])
        ig_hooks = [
            "Save this for later.",
            "Share this with someone who needs it.",
            "Tag a friend who needs to hear this.",
            "Double tap if you agree.",
        ]
        caption = (
            f"{title}\n\n"
            f"{random.choice(ig_hooks)}\n\n"
            f"Follow @theaidollar for daily money tips that actually work.\n"
            f"New videos every single day.\n\n"
            f"#Finance #Money #PersonalFinance #Investing "
            f"#FinanceTips #WealthBuilding #FinancialLiteracy "
            f"#Reels #MoneyTips #FinancialFreedom "
            f"#MoneyHacks #InvestingTips #DebtFree "
            f"#FinancialEducation #MoneySavingTips {kw_tags}"
        )

        media = cl.clip_upload(video_path, caption=caption)
        print(f"[OK] Instagram Reel posted! ID: {media.pk}")

        try:
            cl.dump_settings(session_file)
        except Exception:
            pass

        return True

    except Exception as e:
        print(f"[ERR] Instagram error: {e}")
        return False


def upload_to_facebook(video_path, title, keywords=None):
    """Upload video to Facebook Page as Reel"""
    page_token = os.getenv("FACEBOOK_PAGE_TOKEN", "")
    page_id = os.getenv("FACEBOOK_PAGE_ID", "")
    if not page_token or not page_id:
        print("[SKIP] Facebook: FACEBOOK_PAGE_TOKEN or FACEBOOK_PAGE_ID not set")
        return False

    try:
        kw_tags = " ".join(f"#{k.replace(' ', '')}" for k in (keywords or [])[:5])
        description = (
            f"{title}\n\n"
            f"Like + Follow The AI Dollar for daily money education.\n"
            f"New shorts and deep dives every day.\n\n"
            f"#Finance #Money #PersonalFinance #Investing "
            f"#FinanceTips #WealthBuilding #FinancialLiteracy "
            f"#MoneyHacks #FinancialFreedom #DebtFree "
            f"#InvestingForBeginners #MoneyTips {kw_tags}"
        )

        print("[UPLOAD] Facebook: uploading reel...")
        init_url = f"https://graph.facebook.com/v18.0/{page_id}/video_reels"
        init_resp = requests.post(init_url, data={
            "upload_phase": "start",
            "access_token": page_token,
        })
        if init_resp.status_code != 200:
            print(f"[ERR] Facebook init failed: {init_resp.text}")
            return False

        video_id = init_resp.json().get("video_id")

        upload_url = f"https://rupload.facebook.com/video-upload/v18.0/{video_id}"
        file_size = os.path.getsize(video_path)
        with open(video_path, "rb") as f:
            upload_resp = requests.post(upload_url, data=f, headers={
                "Authorization": f"OAuth {page_token}",
                "offset": "0",
                "file_size": str(file_size),
                "Content-Type": "application/octet-stream",
            })
        if upload_resp.status_code != 200:
            print(f"[ERR] Facebook upload failed: {upload_resp.text}")
            return False

        publish_resp = requests.post(init_url, data={
            "upload_phase": "finish",
            "access_token": page_token,
            "video_id": video_id,
            "title": title[:100],
            "description": description,
        })
        if publish_resp.status_code == 200:
            print(f"[OK] Facebook Reel posted! Video ID: {video_id}")
            return True
        else:
            print(f"[ERR] Facebook publish failed: {publish_resp.text}")
            return False

    except Exception as e:
        print(f"[ERR] Facebook error: {e}")
        return False


def post_video(is_series_part=False, series_name="", part_num=0):
    """Generate and post video to YouTube + TikTok"""
    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] POSTING VIDEO{' [SERIES PART]' if is_series_part else ''}")
    print(f"{'='*50}\n")

    try:
        print("[STEP 1] Generating video...")
        result = generate_daily_video()

        if result['status'] != 'success':
            print(f"[ERR] Video generation failed: {result.get('message','')}")
            return

        video_path = result['video']
        title      = result['title']
        script     = result['script']
        keywords   = result.get('keywords', [])
        print(f"[OK] Video generated: {title}")

        print(f"\n[STEP 2] Uploading to YouTube...")
        youtube_success = upload_to_youtube(video_path, title, script, is_short=True, keywords=keywords)

        print(f"\n[STEP 3] Uploading to TikTok...")
        tiktok_success = upload_to_tiktok(video_path, title, keywords=keywords)

        with open("last_post_time.txt", "w") as f:
            f.write(str(time.time()))

        print(f"\n{'='*50}")
        print(f"[DONE] POSTING COMPLETE")
        print(f"   YouTube:   {'posted' if youtube_success else 'FAILED'}")
        print(f"   TikTok:    {'posted' if tiktok_success else 'FAILED'}")
        print(f"{'='*50}\n")

    except Exception as e:
        print(f"[ERR] Error in post_video: {e}")
        import traceback
        traceback.print_exc()


def post_long_video():
    """Generate and post a long-form video to YouTube + TikTok"""
    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] POSTING LONG-FORM VIDEO")
    print(f"{'='*50}\n")

    try:
        print("[STEP 1] Generating long-form video...")
        result = generate_long_video()

        if result['status'] != 'success':
            print(f"[ERR] Long video generation failed: {result.get('message','')}")
            return

        video_path = result['video']
        title      = result['title']
        script     = result['script']
        keywords   = result.get('keywords', [])
        thumb      = result.get('thumbnail')
        print(f"[OK] Long video generated: {title}")

        print(f"\n[STEP 2] Uploading to YouTube (long-form)...")
        youtube_success = upload_to_youtube(video_path, title, script, is_short=False, keywords=keywords, thumbnail_path=thumb)

        print(f"\n[STEP 3] Uploading to TikTok...")
        tiktok_success = upload_to_tiktok(video_path, title, keywords=keywords)

        with open("last_post_time.txt", "w") as f:
            f.write(str(time.time()))

        print(f"\n{'='*50}")
        print(f"[DONE] LONG-FORM POSTING COMPLETE")
        print(f"   YouTube:   {'posted' if youtube_success else 'FAILED'}")
        print(f"   TikTok:    {'posted' if tiktok_success else 'FAILED'}")
        print(f"{'='*50}\n")

    except Exception as e:
        print(f"[ERR] Error in post_long_video: {e}")
        import traceback
        traceback.print_exc()


def keep_alive():
    """Self-ping to prevent Render free tier from spinning down"""
    try:
        requests.get("https://the-ai-dollar.onrender.com/", timeout=10)
    except Exception:
        pass


def upload_to_tiktok(video_path, title, keywords=None):
    """Upload video to TikTok using direct API with session cookie"""
    tiktok_session = os.getenv("TIKTOK_SESSION_ID", "")
    if not tiktok_session:
        print("[SKIP] TikTok: TIKTOK_SESSION_ID not set")
        return False

    try:
        import requests as req

        kw_tags = " ".join(f"#{k.replace(' ', '')}" for k in (keywords or [])[:3])
        caption = (
            f"{title[:60]} "
            f"#moneytok #fintok #investing #finance #personalfinance "
            f"#moneytips #financialfreedom #wealthbuilding "
            f"#learnontiktok #fyp #viral {kw_tags}"
        )[:150]

        cookies = {"sessionid": tiktok_session}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        # Step 1: Get upload URL
        print("[TikTok] Getting upload URL...")
        init_url = "https://www.tiktok.com/api/v1/video/upload/auth/"
        sess = req.Session()
        sess.cookies.update(cookies)
        sess.headers.update(headers)

        # Use creator center upload endpoint
        upload_page = sess.get("https://www.tiktok.com/creator#/upload", timeout=30)
        print(f"[TikTok] Creator page status: {upload_page.status_code}")

        # Direct video publish via internal API
        file_size = os.path.getsize(video_path)
        print(f"[TikTok] Video size: {file_size / 1024 / 1024:.1f}MB")

        with open(video_path, 'rb') as f:
            video_data = f.read()

        # Upload video chunk
        upload_url = "https://www.tiktok.com/upload/video/"
        files = {"video": (os.path.basename(video_path), video_data, "video/mp4")}
        data = {"caption": caption}

        resp = sess.post(upload_url, files=files, data=data, timeout=120)
        print(f"[TikTok] Upload response: {resp.status_code}")

        if resp.status_code == 200:
            print(f"[OK] TikTok posted! Title: {title[:50]}")
            return True
        else:
            print(f"[ERR] TikTok upload failed: {resp.status_code} - {resp.text[:200]}")
            return False

    except Exception as e:
        print(f"[ERR] TikTok error: {e}")
        return False


def schedule_jobs():
    # SHORTS ONLY — discovery engine for small channels
    # Shorts get shown on the Shorts shelf to non-subscribers
    # 6 per day, spaced across US peak hours (times in UTC)
    schedule.every().day.at("06:00").do(post_video)   # US East 2am — early birds
    schedule.every().day.at("10:00").do(post_video)   # US East 6am — early commute
    schedule.every().day.at("13:00").do(post_video)   # US East 9am — mid-morning scroll
    schedule.every().day.at("16:00").do(post_video)   # US East 12pm — lunch break
    schedule.every().day.at("20:00").do(post_video)   # US East 4pm — afternoon break
    schedule.every().day.at("23:30").do(post_video)   # US East 7:30pm — prime time

    schedule.every(10).minutes.do(keep_alive)
    print("[OK] Schedule: 6 Shorts/day — growth mode (no long-form until 500+ subs)")
    print("[OK] Shorts = discovery engine for non-subscribers")
    print("[OK] Self-ping every 10 min to prevent Render spin-down")


def main():
    print("\n[START] THE AI DOLLAR - AUTOMATION STARTED")
    print("=" * 50)
    print(f"Started at: {datetime.now()}")
    print("=" * 50)

    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    schedule_jobs()

    print("\n[NOW] Posting first short on startup...\n")
    try:
        post_video()
    except Exception as e:
        print(f"[ERR] Startup post error: {e}")

    print("\n[SCHED] Scheduler running (6 shorts/day — growth mode + self-ping every 10 min)...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n[STOP] Stopped")


if __name__ == "__main__":
    main()
