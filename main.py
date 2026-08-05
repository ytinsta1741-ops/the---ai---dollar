#!/usr/bin/env python3
"""
The AI Dollar - Complete Automation
Generates videos, uploads to YouTube, posts to Instagram
Runs on schedule: 6 slots optimized for US peak hours
"""

import os
import sys
import time
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


def upload_to_youtube(video_path, title, description, is_short=True, keywords=None):
    """Upload video to YouTube using OAuth refresh token"""
    try:
        refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN", "")
        if not refresh_token:
            print("[WARN] YOUTUBE_REFRESH_TOKEN not set -- skipping YouTube")
            return False

        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

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
            "stock market for beginners", "save money", "make money",
            "budget tips", "debt free", "credit score",
            "side hustle", "financial freedom", "money advice 2026",
            "finance tips", "get rich", "TheAIDollar",
            "money hacks", "rich vs poor", "compound interest",
            "index funds", "roth ira", "how to save money",
        ]
        yt_tags = topic_tags + [t for t in base_tags if t.lower() not in [k.lower() for k in topic_tags]]
        import re
        yt_tags = [re.sub(r'[<>]', '', t).strip() for t in yt_tags if t.strip()]
        yt_tags = [t[:100] for t in yt_tags if t]
        total = 0
        trimmed = []
        for t in yt_tags:
            if total + len(t) > 480:
                break
            trimmed.append(t)
            total += len(t)
        yt_tags = trimmed

        kw_line = ", ".join(topic_tags[:5]) if topic_tags else "money tips, finance, investing"

        if is_short:
            yt_title = title[:100]
            yt_desc = (
                f"{title}\n\n"
                f"This changes everything about how you think about money.\n\n"
                f"WATCH NEXT: Check our channel for the full breakdown!\n\n"
                f"COMMENT below: What's YOUR #1 money question?\n"
                f"SUBSCRIBE for daily money lessons (new video every few hours)\n\n"
                f"#Shorts #Finance #Money #Investing #PersonalFinance "
                f"#WealthBuilding #FinancialFreedom #MoneyTips #FinanceTips "
                f"#HowToGetRich #PassiveIncome #DebtFree #SideHustle "
                f"#FinancialLiteracy #MakeMoney #MoneyHacks #CompoundInterest "
                f"#InvestingForBeginners #BudgetTips #TheAIDollar #MoneyAdvice "
                f"#RichVsPoor #WealthTips #StockMarket #IndexFunds "
                f"#MillionaireMindset #MoneyMindset #FinancialEducation "
                f"#MoneyMotivation #WealthSecrets"
            )
            yt_tags.append("Shorts")
        else:
            yt_title = title[:100]
            yt_desc = (
                f"{title} | The AI Dollar\n\n"
                f"In this video, you'll learn everything you need to know about {kw_line}.\n\n"
                f"TIMESTAMPS:\n"
                f"0:00 - Why this matters RIGHT NOW\n"
                f"0:45 - The core concept (explained simply)\n"
                f"2:30 - Proven strategies from real millionaires\n"
                f"5:15 - Your step-by-step action plan\n"
                f"7:30 - Mistakes that keep people broke\n\n"
                f"If this helped you, SUBSCRIBE and turn on notifications.\n"
                f"We post daily money education that schools don't teach.\n\n"
                f"COMMENT your biggest takeaway below!\n"
                f"SHARE with someone who needs to hear this.\n\n"
                f"#Finance #Money #PersonalFinance #Investing #WealthBuilding "
                f"#FinancialFreedom #MoneyTips #FinanceTips #FinancialLiteracy "
                f"#HowToGetRich #StockMarket #PassiveIncome #DebtFree "
                f"#Budgeting #MakeMoney #InvestingForBeginners #TheAIDollar "
                f"#MoneyHacks #CompoundInterest #MillionaireMindset #WealthSecrets "
                f"#IndexFunds #MoneyMotivation #FinancialEducation"
            )

        body = {
            "snippet": {
                "title": yt_title,
                "description": yt_desc,
                "tags": yt_tags,
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

        video_id = response.get("id", "")
        print(f"[OK] YouTube uploaded! https://youtube.com/watch?v={video_id}")
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

        kw_tags = " ".join(f"#{k.replace(' ', '')}" for k in (keywords or []))
        caption = (
            f"{title}\n\n"
            f"Follow @theaidollar for daily finance tips!\n\n"
            f"#Finance #Money #PersonalFinance #Investing "
            f"#FinanceTips #WealthBuilding #FinancialLiteracy "
            f"#Reels #MoneyTips #FinancialFreedom {kw_tags}"
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
        kw_tags = " ".join(f"#{k.replace(' ', '')}" for k in (keywords or []))
        description = (
            f"{title}\n\n"
            f"Follow The AI Dollar for daily finance education!\n\n"
            f"#Finance #Money #PersonalFinance #Investing "
            f"#FinanceTips #WealthBuilding #FinancialLiteracy {kw_tags}"
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
    """Generate and post video to YouTube + Instagram + Facebook
    is_series_part: True adds series info to title for binge-watching"""
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

        print(f"\n[STEP 3] Uploading to Instagram...")
        instagram_success = upload_to_instagram(video_path, title, keywords=keywords)

        print(f"\n[STEP 4] Uploading to Facebook...")
        facebook_success = upload_to_facebook(video_path, title, keywords=keywords)

        print(f"\n[STEP 5] Uploading to TikTok...")
        tiktok_success = upload_to_tiktok(video_path, title, keywords=keywords)

        with open("last_post_time.txt", "w") as f:
            f.write(str(time.time()))

        print(f"\n{'='*50}")
        print(f"[DONE] POSTING COMPLETE")
        print(f"   YouTube:   {'posted' if youtube_success else 'skipped'}")
        print(f"   Instagram: {'posted' if instagram_success else 'skipped'}")
        print(f"   Facebook:  {'posted' if facebook_success else 'skipped'}")
        print(f"   TikTok:    {'posted' if tiktok_success else 'skipped'}")
        print(f"{'='*50}\n")

    except Exception as e:
        print(f"[ERR] Error in post_video: {e}")
        import traceback
        traceback.print_exc()


def post_long_video():
    """Generate and post a 2-3 minute long-form video to YouTube + Instagram + Facebook"""
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
        print(f"[OK] Long video generated: {title}")

        print(f"\n[STEP 2] Uploading to YouTube (long-form)...")
        youtube_success = upload_to_youtube(video_path, title, script, is_short=False, keywords=keywords)

        print(f"\n[STEP 3] Uploading to Instagram...")
        instagram_success = upload_to_instagram(video_path, title, keywords=keywords)

        print(f"\n[STEP 4] Uploading to Facebook...")
        facebook_success = upload_to_facebook(video_path, title, keywords=keywords)

        print(f"\n[STEP 5] Uploading to TikTok...")
        tiktok_success = upload_to_tiktok(video_path, title, keywords=keywords)

        with open("last_post_time.txt", "w") as f:
            f.write(str(time.time()))

        print(f"\n{'='*50}")
        print(f"[DONE] LONG-FORM POSTING COMPLETE")
        print(f"   YouTube:   {'posted' if youtube_success else 'skipped'}")
        print(f"   Instagram: {'posted' if instagram_success else 'skipped'}")
        print(f"   Facebook:  {'posted' if facebook_success else 'skipped'}")
        print(f"   TikTok:    {'posted' if tiktok_success else 'skipped'}")
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

        kw_tags = " ".join(f"#{k.replace(' ', '')}" for k in (keywords or []))
        caption = (
            f"{title[:70]} "
            f"#moneytok #fintok #investing #finance #personalfinance "
            f"#moneytips #financialfreedom #wealthbuilding #sidehustle "
            f"#learnontiktok {kw_tags}"
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
    # LONG-FORM (3x daily = watch time for monetization)
    # Post BEFORE peak hours so they're indexed when viewers arrive
    schedule.every().day.at("06:30").do(post_long_video)  # Ready for morning viewers
    schedule.every().day.at("13:30").do(post_long_video)  # Ready for afternoon viewers
    schedule.every().day.at("19:30").do(post_long_video)  # Ready for evening viewers

    # SHORTS (8x daily = more algorithm lottery tickets)
    # YouTube Shorts peak: 6-9am, 12-2pm, 7-10pm US time
    schedule.every().day.at("06:00").do(post_video)   # Early birds (US East 6am)
    schedule.every().day.at("08:30").do(post_video)   # Morning commute
    schedule.every().day.at("11:00").do(post_video)   # Pre-lunch scroll
    schedule.every().day.at("13:00").do(post_video)   # Lunch break peak
    schedule.every().day.at("16:00").do(post_video)   # Afternoon slump scroll
    schedule.every().day.at("19:00").do(post_video)   # Evening prime time
    schedule.every().day.at("21:00").do(post_video)   # Night scroll (peak Shorts)
    schedule.every().day.at("23:30").do(post_video)   # Late night + EU/Asia morning

    schedule.every(10).minutes.do(keep_alive)
    print("[OK] Schedule: 3 Long-form + 8 Shorts = 11 posts/day")
    print("[OK] Long-form = watch hours for monetization (4000h goal)")
    print("[OK] Shorts = 8 daily algorithm lottery tickets")
    print("[OK] Self-ping every 10 min to prevent Render spin-down")


def main():
    print("\n[START] THE AI DOLLAR - AUTOMATION STARTED")
    print("=" * 50)
    print(f"Started at: {datetime.now()}")
    print("=" * 50)

    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    schedule_jobs()

    print("\n[NOW] Posting first short + long-form on startup...\n")
    try:
        post_video()
        time.sleep(30)
        post_long_video()
    except Exception as e:
        print(f"[ERR] Startup post error: {e}")

    print("\n[SCHED] Scheduler running (3 long + 8 shorts = 11 posts/day + self-ping every 10 min)...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n[STOP] Stopped")


if __name__ == "__main__":
    main()
