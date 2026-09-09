"""Publish a video file at a URL Make.com (and therefore Instagram) can fetch.

The old path served the file from the Render web service — that only worked
while an always-on service existed, and dies when the pipeline moves to
GitHub Actions runs. This module gives publish_video_url() two backends and
picks the one the environment is configured for:

  Backend A — GitHub Releases (used when GH_RELEASE_UPLOAD is truthy).
  A workflow run creates a release, uploads the MP4 as an asset, and returns
  its public download URL. Assets on public repos are downloadable without a
  token, which is exactly what Instagram's Graph API needs.

  Backend B — Render static host (the historical setup). Files sit in the
  running Render instance's ./videos and are served by main.py's / handler.

Nothing else in the code needs to know which one is in play."""

import os
import subprocess
import time


def _github_release_upload(video_path):
    """Upload the MP4 as a GitHub release asset and return its download URL.

    Runs on a GitHub Actions runner where `gh` and GITHUB_TOKEN are provided
    automatically. The release tag is derived from the current UTC minute so
    a same-day retry gets its own tag rather than colliding."""
    repo = os.getenv("GITHUB_REPOSITORY")
    if not repo:
        raise RuntimeError(
            "GH_RELEASE_UPLOAD is set but GITHUB_REPOSITORY is not — this "
            "path only runs inside GitHub Actions."
        )

    tag = "video-" + time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    title = "AI Dollar auto-post " + tag[6:]

    # Create the release. --generate-notes is skipped because notes on a
    # binary-only release are noise. --latest is skipped so scheduled
    # uploads do not fight over the "Latest" flag; every release is its own.
    subprocess.run(
        ["gh", "release", "create", tag,
         "--title", title,
         "--notes", "Automated upload for Instagram fetch by Make.com."],
        check=True, capture_output=True, text=True,
    )
    # Upload the file as an asset with a fixed name so the URL is
    # predictable per-tag.
    asset_name = "video.mp4"
    subprocess.run(
        ["gh", "release", "upload", tag,
         f"{video_path}#{asset_name}"],
        check=True, capture_output=True, text=True,
    )
    return f"https://github.com/{repo}/releases/download/{tag}/{asset_name}"


def publish_video_url(video_path, public_base_url=None):
    """Return a URL that resolves to `video_path` for external services.

    On a GitHub Actions run this uploads to Releases and returns that URL.
    Elsewhere it assumes the caller's Render service serves ./videos at
    `public_base_url` and returns that URL as before."""
    if os.getenv("GH_RELEASE_UPLOAD", "").lower() in ("1", "true", "yes"):
        return _github_release_upload(video_path)

    if not public_base_url:
        raise RuntimeError(
            "Neither GH_RELEASE_UPLOAD nor a public_base_url is set — no way "
            "to hand this video to Make.com."
        )
    return f"{public_base_url}/media/{os.path.basename(video_path)}"
