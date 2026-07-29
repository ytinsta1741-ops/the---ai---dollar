#!/usr/bin/env python3
"""
Instagram posting using instagrapi (no browser needed - works on Render)
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()


def post_to_instagram(video_path, caption):
    """Post video to Instagram using instagrapi (no browser required)"""
    username = os.getenv("INSTAGRAM_USERNAME", "")
    password = os.getenv("INSTAGRAM_PASSWORD", "")

    if not username or not password or password == "your_password_here":
        print("⚠️  Instagram credentials not set in .env — skipping")
        return False

    if not video_path or not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False

    try:
        from instagrapi import Client
        from instagrapi.exceptions import LoginRequired

        cl = Client()
        cl.delay_range = [1, 3]

        session_file = "instagram_session.json"

        if os.path.exists(session_file):
            try:
                cl.load_settings(session_file)
                cl.login(username, password)
                print("✅ Instagram: resumed session")
            except LoginRequired:
                cl = Client()
                cl.login(username, password)
                cl.dump_settings(session_file)
                print("✅ Instagram: logged in fresh")
        else:
            cl.login(username, password)
            cl.dump_settings(session_file)
            print("✅ Instagram: logged in")

        print(f"📤 Uploading reel to Instagram...")
        media = cl.video_upload(
            video_path,
            caption=caption
        )

        print(f"✅ Instagram posted! Media ID: {media.pk}")
        return True

    except ImportError:
        print("❌ instagrapi not installed — add it to requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Instagram error: {e}")
        return False
