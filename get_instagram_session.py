#!/usr/bin/env python3
"""
Run this ONCE on your computer to generate an Instagram session.
It logs in, handles any verification challenge, and saves the session
as a base64 string you can paste into Render env vars.
"""

import sys
import json
import base64

try:
    from instagrapi import Client
except ImportError:
    print("Installing instagrapi...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "instagrapi", "Pillow"])
    from instagrapi import Client


def main():
    print("=" * 50)
    print("INSTAGRAM SESSION GENERATOR")
    print("=" * 50)

    username = input("\nEnter your Instagram username: ").strip()
    password = input("Enter your Instagram password: ").strip()

    print(f"\nLogging in as @{username}...")

    cl = Client()
    cl.delay_range = [1, 3]

    try:
        cl.login(username, password)
        print("Login successful!")
    except Exception as e:
        error_msg = str(e)
        if "challenge" in error_msg.lower() or "verification" in error_msg.lower():
            print("\nInstagram wants to verify your identity.")
            print("Check your email/phone for a code from Instagram.")
            code = input("Enter the verification code: ").strip()
            try:
                cl.challenge_resolve(code)
                print("Verification successful!")
            except Exception:
                print("Trying alternative challenge method...")
                cl = Client()
                cl.delay_range = [1, 3]
                cl.login(username, password, verification_code=code)
                print("Login successful!")
        else:
            print(f"Login failed: {e}")
            return

    session_file = "ig_session.json"
    cl.dump_settings(session_file)

    with open(session_file, "r") as f:
        session_data = f.read()

    encoded = base64.b64encode(session_data.encode()).decode()

    print("\n" + "=" * 60)
    print("SUCCESS! Copy the value below and add it to Render.com as:")
    print("  Name:  INSTAGRAM_SESSION")
    print("  Value: [the text below]")
    print("=" * 60)
    print(encoded[:100] + "..." if len(encoded) > 100 else encoded)

    with open("ig_session_b64.txt", "w") as f:
        f.write(encoded)

    print(f"\nFull session saved to ig_session_b64.txt")
    print("Copy the ENTIRE contents of that file into Render env var INSTAGRAM_SESSION")
    print(f"\nAlso make sure these env vars are set on Render:")
    print(f"  INSTAGRAM_USERNAME = {username}")
    print(f"  INSTAGRAM_PASSWORD = {password}")


if __name__ == "__main__":
    main()
