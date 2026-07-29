#!/usr/bin/env python3
"""
Instagram posting using instagrapi (no browser needed - works on Render)
"""

import os
import re
from dotenv import load_dotenv

load_dotenv()


def _patch_instagrapi_file():
    """Patch instagrapi/types.py on disk to add check_fields=False to all validators"""
    try:
        import importlib.util
        spec = importlib.util.find_spec('instagrapi')
        if not spec or not spec.origin:
            return
        types_path = os.path.join(os.path.dirname(spec.origin), 'types.py')
        if not os.path.exists(types_path):
            return
        with open(types_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'check_fields=False' in content:
            return  # Already patched
        # Add check_fields=False to all @validator decorators
        patched = re.sub(
            r"@validator\(([^)]+)\)",
            lambda m: m.group(0) if 'check_fields' in m.group(0)
                      else f"@validator({m.group(1)}, check_fields=False)",
            content
        )
        if patched != content:
            with open(types_path, 'w', encoding='utf-8') as f:
                f.write(patched)
            print("✅ Patched instagrapi types.py (check_fields=False)")
    except Exception as e:
        print(f"⚠️ instagrapi patch warning: {e}")


# Patch the file BEFORE ever importing instagrapi
_patch_instagrapi_file()


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
