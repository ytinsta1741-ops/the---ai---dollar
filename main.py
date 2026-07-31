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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from video_generator import generate_daily_video
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


def upload_to_youtube(video_path, title, description):
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

        body = {
            "snippet": {
                "title": title[:100] + " #Shorts",
                "description": f"{description}\n\nLearn finance in 60 seconds. New video every few hours!\n\nSubscribe to The AI Dollar for daily finance education.\n\n#Finance #Money #PersonalFinance #Investing #Shorts #FinanceTips #MoneyTips #WealthBuilding #FinancialLiteracy #MoneyManagement #StockMarket #Budgeting #DebtFree #PassiveIncome #TheAIDollar",
                "tags": ["Finance", "Personal Finance", "Money Tips", "Investing For Beginners", "Financial Literacy", "Money Management", "Stock Market", "Budgeting Tips", "Wealth Building", "Passive Income", "Credit Score", "Debt Free", "Savings Tips", "Financial Education", "Money Advice", "TheAIDollar", "Shorts"],
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
        print(f"[OK] Video generated: {title}")

        print(f"\n[STEP 2] Uploading to YouTube...")
        youtube_success = upload_to_youtube(video_path, title, script)

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


def schedule_jobs():
    schedule.every().day.at("10:00").do(post_video)  # 10 AM KSA = 3 AM EST (UK morning)
    schedule.every().day.at("15:00").do(post_video)  # 3 PM KSA = 8 AM EST (US morning)
    schedule.every().day.at("20:00").do(post_video)  # 8 PM KSA = 1 PM EST (US lunch)
    schedule.every().day.at("23:00").do(post_video)  # 11 PM KSA = 4 PM EST (US after work)
    schedule.every().day.at("02:00").do(post_video)  # 2 AM KSA = 7 PM EST (US PRIME TIME)
    schedule.every().day.at("05:00").do(post_video)  # 5 AM KSA = 10 PM EST (US late night)
    print("[OK] Jobs scheduled: 10AM | 3PM | 8PM | 11PM | 2AM | 5AM KSA (optimized for US peak)")


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

    print("\n[SCHED] Scheduler running (10AM | 3PM | 8PM | 11PM | 2AM | 5AM KSA)...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n[STOP] Stopped")


if __name__ == "__main__":
    main()
