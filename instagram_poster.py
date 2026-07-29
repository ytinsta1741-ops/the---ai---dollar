#!/usr/bin/env python3
"""
Instagram posting using instagrapi (no browser needed - works on Render)
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Patch pydantic BEFORE importing instagrapi so validators on missing fields don't crash
def _patch_pydantic():
    try:
        from pydantic.class_validators import ValidatorDecoratorInfo
        _orig = ValidatorDecoratorInfo.__init__
        def _new(self, *args, **kwargs):
            kwargs['check_fields'] = False
            _orig(self, *args, **kwargs)
        ValidatorDecoratorInfo.__init__ = _new
    except Exception:
        pass

_patch_pydantic()


def post_to_instagram(video_path, caption):
    """Post video to Instagram using instagrapi"""
    username = os.getenv("INSTAGRAM_USERNAME", "")
    password = os.getenv("INSTAGRAM_PASSWORD", "")

    if not username or not password or password == "your_password_here":
        print("⚠️  Instagram credentials not set — skipping")
        return False

    if not video_path or not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False

    try:
        from instagrapi import Client

        cl = Client()
        cl.delay_range = [1, 3]

        session_file = "instagram_session.json"

        if os.path.exists(session_file):
            try:
                cl.load_settings(session_file)
                cl.login(username, password)
                print("✅ Instagram: resumed session")
            except Exception:
                cl = Client()
                cl.delay_range = [1, 3]
                cl.login(username, password)
                cl.dump_settings(session_file)
                print("✅ Instagram: logged in fresh")
        else:
            cl.login(username, password)
            cl.dump_settings(session_file)
            print("✅ Instagram: logged in")

        print("📤 Uploading reel to Instagram...")
        media = cl.video_upload(video_path, caption=caption)
        print(f"✅ Instagram posted! ID: {media.pk}")
        return True

    except Exception as e:
        print(f"❌ Instagram error: {e}")
        import traceback
        traceback.print_exc()
        return False
