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
            "side hustle", "financial freedom", "money advice 2025",
            "finance tips", "get rich", "TheAIDollar",
        ]
        yt_tags = topic_tags + [t for t in base_tags if t.lower() not in [k.lower() for k in topic_tags]]

        kw_line = ", ".join(topic_tags[:5]) if topic_tags else "money tips, finance, investing"

        if is_short:
            yt_title = title[:100] + " #Shorts"
            yt_desc = (
                f"{kw_line} - {title}\n\n"
                f"{description}\n\n"
                f"Want to learn finance in 60 seconds? SUBSCRIBE to The AI Dollar!\n"
                f"New Shorts EVERY FEW HOURS + deep-dive videos DAILY.\n\n"
                f"LIKE this video if you learned something!\n"
                f"COMMENT your biggest money question below!\n"
                f"SHARE with a friend who needs to hear this!\n\n"
                f"#Finance #Money #PersonalFinance #Investing #Shorts "
                f"#FinanceTips #MoneyTips #WealthBuilding #FinancialLiteracy "
                f"#StockMarket #Budgeting #DebtFree #PassiveIncome "
                f"#MoneyManagement #FinancialFreedom #HowToInvest "
                f"#MakeMoneyOnline #SideHustle #CreditScore #TheAIDollar"
            )
            yt_tags.append("Shorts")
        else:
            yt_title = title[:100]
            yt_desc = (
                f"{kw_line} - Complete guide for beginners\n\n"
                f"{description}\n\n"
                f"In this video you'll learn everything about {kw_line}.\n\n"
                f"SUBSCRIBE to The AI Dollar for daily finance education!\n"
                f"New deep-dive videos EVERY DAY + Shorts every few hours.\n\n"
                f"LIKE if this helped you!\n"
                f"COMMENT your #1 finance question!\n"
                f"SHARE with someone who needs financial education!\n\n"
                f"TIMESTAMPS:\n0:00 Introduction\n0:15 Key concepts\n1:00 Strategy\n2:00 Action steps\n\n"
                f"#Finance #Money #PersonalFinance #Investing "
                f"#FinanceTips #WealthBuilding #FinancialLiteracy "
                f"#StockMarket #Budgeting #DebtFree #PassiveIncome "
                f"#FinancialFreedom #HowToInvest #MoneyManagement #TheAIDollar"
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


def post_video():
    """Generate and post video to YouTube + Instagram"""
    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] POSTING VIDEO")
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

        print(f"\n[STEP 3] Instagram...")
        print("[SKIP] Instagram disabled (anti-bot detection blocking automated posts)")
        instagram_success = False

        with open("last_post_time.txt", "w") as f:
            f.write(str(time.time()))

        print(f"\n{'='*50}")
        print(f"[DONE] POSTING COMPLETE")
        print(f"   YouTube:   {'posted' if youtube_success else 'skipped'}")
        print(f"   Instagram: {'posted' if instagram_success else 'skipped'}")
        print(f"{'='*50}\n")

    except Exception as e:
        print(f"[ERR] Error in post_video: {e}")
        import traceback
        traceback.print_exc()


def post_long_video():
    """Generate and post a 2-3 minute long-form video to YouTube"""
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

        with open("last_post_time.txt", "w") as f:
            f.write(str(time.time()))

        print(f"\n{'='*50}")
        print(f"[DONE] LONG-FORM POSTING COMPLETE")
        print(f"   YouTube: {'posted' if youtube_success else 'skipped'}")
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


def schedule_jobs():
    schedule.every().day.at("07:00").do(post_long_video)  # 7 AM UTC = 10 AM KSA -- LONG-FORM VIDEO
    schedule.every().day.at("12:00").do(post_video)  # 12 PM UTC = 3 PM KSA = 8 AM EST
    schedule.every().day.at("17:00").do(post_video)  # 5 PM UTC = 8 PM KSA = 1 PM EST
    schedule.every().day.at("20:00").do(post_video)  # 8 PM UTC = 11 PM KSA = 4 PM EST
    schedule.every().day.at("23:00").do(post_video)  # 11 PM UTC = 2 AM KSA = 7 PM EST
    schedule.every().day.at("02:00").do(post_video)  # 2 AM UTC = 5 AM KSA = 10 PM EST
    schedule.every(10).minutes.do(keep_alive)
    print("[OK] Schedule: 5 Shorts + 1 Long-form daily (US peak hours)")
    print("[OK] Self-ping every 10 min to prevent Render spin-down")


def main():
    print("\n[START] THE AI DOLLAR - AUTOMATION STARTED")
    print("=" * 50)
    print(f"Started at: {datetime.now()}")
    print("=" * 50)

    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    schedule_jobs()

    last_post_file = "last_post_time.txt"
    should_post = True
    if os.path.exists(last_post_file):
        try:
            with open(last_post_file) as f:
                last = float(f.read().strip())
            if time.time() - last < 3600:
                print("[SKIP] Posted less than 1 hour ago -- waiting for next schedule")
                should_post = False
        except Exception:
            pass

    if should_post:
        print("\n[NOW] Posting first video now...\n")
        post_video()

    print("\n[SCHED] Scheduler running (6 posts/day UTC + self-ping every 10 min)...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n[STOP] Stopped")


if __name__ == "__main__":
    main()
