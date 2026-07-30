#!/usr/bin/env python3
"""
Instagram posting using instagrapi (no browser needed - works on Render)
"""

import os
import re
import json
import base64
import tempfile
from dotenv import load_dotenv

load_dotenv()


def _patch_pydantic_for_instagrapi():
    """Monkey-patch pydantic to handle instagrapi's untyped fields"""
    try:
        import pydantic.fields
        _orig = pydantic.fields.ModelField._set_default_and_type
        def _safe_set(self):
            try:
                _orig(self)
            except Exception:
                from typing import Any
                self.type_ = Any
                self.outer_type_ = Any
                if self.default is None:
                    self.required = False
        pydantic.fields.ModelField._set_default_and_type = _safe_set
        print("✅ Patched pydantic for instagrapi compatibility")
    except Exception as e:
        print(f"⚠️ pydantic patch warning: {e}")


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
            return
        patched = re.sub(
            r'\bvalidator\(([^)]+)\)',
            lambda m: m.group(0) if 'check_fields' in m.group(0)
                      else f"validator({m.group(1)}, check_fields=False)",
            content
        )
        if patched != content:
            with open(types_path, 'w', encoding='utf-8') as f:
                f.write(patched)
            print("✅ Patched instagrapi types.py (check_fields=False)")
        else:
            print("⚠️ instagrapi patch: no changes made")
    except Exception as e:
        print(f"⚠️ instagrapi patch warning: {e}")


_patch_pydantic_for_instagrapi()
_patch_instagrapi_file()


def _load_session_from_env():
    """Load Instagram session from INSTAGRAM_SESSION env var (base64-encoded JSON)"""
    session_b64 = os.getenv("INSTAGRAM_SESSION", "")
    if not session_b64:
        return None
    try:
        session_json = base64.b64decode(session_b64).decode()
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        tmp.write(session_json)
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"⚠️ Failed to decode INSTAGRAM_SESSION: {e}")
        return None


def post_to_instagram(video_path, caption):
    """Post video to Instagram using instagrapi"""
    username = os.getenv("INSTAGRAM_USERNAME", "") or os.getenv("INSTAGRAMUSERNAME", "")
    password = os.getenv("INSTAGRAM_PASSWORD", "") or os.getenv("INSTAGRAMPASSWORD", "")

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

        logged_in = False

        session_file = _load_session_from_env()
        if session_file:
            try:
                cl.load_settings(session_file)
                cl.login(username, password)
                logged_in = True
                print("✅ Instagram: resumed session from env var")
            except Exception as e:
                print(f"⚠️ Session from env failed ({e}), trying fresh login...")
                cl = Client()
                cl.delay_range = [1, 3]
            finally:
                try:
                    os.unlink(session_file)
                except Exception:
                    pass

        if not logged_in and os.path.exists("instagram_session.json"):
            try:
                cl.load_settings("instagram_session.json")
                cl.login(username, password)
                logged_in = True
                print("✅ Instagram: resumed session from file")
            except Exception:
                cl = Client()
                cl.delay_range = [1, 3]

        if not logged_in:
            cl.login(username, password)
            cl.dump_settings("instagram_session.json")
            print("✅ Instagram: logged in fresh")

        print("📤 Uploading reel to Instagram...")
        try:
            media = cl.clip_upload(video_path, caption=caption)
        except Exception as e:
            print(f"⚠️ clip_upload failed ({e}), trying video_upload...")
            media = cl.video_upload(video_path, caption=caption)
        print(f"✅ Instagram posted! ID: {media.pk}")

        try:
            cl.dump_settings("instagram_session.json")
        except Exception:
            pass

        return True

    except Exception as e:
        print(f"❌ Instagram error: {e}")
        import traceback
        traceback.print_exc()
        return False
