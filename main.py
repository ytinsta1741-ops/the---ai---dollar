#!/usr/bin/env python3
"""
The AI Dollar - Complete Automation
Generates videos, uploads to YouTube, posts to Instagram
Runs on schedule: 4 PM, 8 PM, 1 AM KSA
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
    print(f"✅ Health server running on port {port}")
    server.serve_forever()


def upload_to_youtube(video_path, title, description):
    """Upload video to YouTube using OAuth refresh token"""
    try:
        refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN", "")
        if not refresh_token:
            print("⚠️  YOUTUBE_REFRESH_TOKEN not set — skipping YouTube")
            return False

        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        CLIENT_ID     = os.getenv("YOUTUBE_CLIENT_ID", "")
        CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
        if not CLIENT_ID or not CLIENT_SECRET:
            print("⚠️  YOUTUBE_CLIENT_ID or YOUTUBE_CLIENT_SECRET not set — skipping YouTube")
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
                "title": title[:100],
                "description": f"{description}\n\nLearn finance in 60 seconds. Subscribe for daily tips!\n\n#Finance #Money #PersonalFinance #Investing #TheAIDollar",
                "tags": ["Finance", "Personal Finance", "Money", "Investing", "Credit Score", "Budgeting", "Stocks", "TheAIDollar"],
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
                print(f"📤 YouTube: {int(status.progress() * 100)}% uploaded")

        video_id = response.get("id", "")
        print(f"✅ YouTube uploaded! https://youtube.com/watch?v={video_id}")
        return True

    except Exception as e:
        print(f"❌ YouTube error: {e}")
        import traceback
        traceback.print_exc()
        return False


def post_video():
    """Generate and post video to YouTube + Instagram"""
    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] POSTING VIDEO")
    print(f"{'='*50}\n")

    try:
        print("1️⃣  Generating video...")
        result = generate_daily_video()

        if result['status'] != 'success':
            print(f"❌ Video generation failed: {result.get('message','')}")
            return

        video_path = result['video']
        title      = result['title']
        script     = result['script']
        print(f"✅ Video generated: {title}")

        print(f"\n2️⃣  Uploading to YouTube...")
        youtube_success = upload_to_youtube(video_path, title, script)

        print(f"\n3️⃣  Posting to Instagram...")
        caption = (
            f"{title}\n\n"
            f"Follow @theaidollar1741 for daily finance education!\n\n"
            f"#Finance #Money #PersonalFinance #Investing #FinanceTips #TheAIDollar"
        )
        instagram_success = post_to_instagram(video_path, caption)

        with open("last_post_time.txt", "w") as f:
            f.write(str(time.time()))

        print(f"\n{'='*50}")
        print(f"✅ POSTING COMPLETE")
        print(f"   YouTube:   {'✅ posted' if youtube_success else '⏭️ skipped'}")
        print(f"   Instagram: {'✅ posted' if instagram_success else '⏭️ skipped'}")
        print(f"{'='*50}\n")

    except Exception as e:
        print(f"❌ Error in post_video: {e}")
        import traceback
        traceback.print_exc()


def schedule_jobs():
    schedule.every().day.at("16:00").do(post_video)  # 4 PM KSA
    schedule.every().day.at("20:00").do(post_video)  # 8 PM KSA
    schedule.every().day.at("01:00").do(post_video)  # 1 AM KSA
    print("✅ Jobs scheduled: 4 PM | 8 PM | 1 AM KSA")


def main():
    print("\n🚀 THE AI DOLLAR - AUTOMATION STARTED")
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
            if time.time() - last < 7200:
                print("⏭️  Posted less than 2 hours ago — waiting for next schedule")
                should_post = False
        except Exception:
            pass

    if should_post:
        print("\n⏱️  Posting first video now...\n")
        post_video()

    print("\n⏰ Scheduler running (4 PM, 8 PM, 1 AM KSA)...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n❌ Stopped")


if __name__ == "__main__":
    main()
