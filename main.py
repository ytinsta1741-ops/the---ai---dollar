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

        CLIENT_ID     = "521651303810-e7elq5l12oo6ju5jq9iah4hf2l914mof.apps.googleusercontent.com"
        CLIENT_SECRET = "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"

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
                "description": f"{description}\n\n#AI #Money #Finance #SideHustle #TheAIDollar",
                "tags": ["AI", "Money", "Finance", "SideHustle", "ChatGPT", "PassiveIncome"],
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
            f"Subscribe to The AI Dollar for daily finance + AI tips!\n\n"
            f"#AI #Money #Finance #SideHustle #ChatGPT #PassiveIncome #TheAIDollar"
        )
        instagram_success = post_to_instagram(video_path, caption)

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
