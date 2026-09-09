# Running the pipeline on GitHub Actions

This is the checklist for switching over from the Render service to GitHub
Actions. All values come from the local `.env`; do not commit `.env`.

## 1. Add repository secrets

Repo → **Settings → Secrets and variables → Actions → New repository
secret**, one entry each. Names must match exactly.

| Secret name                  | Where to find the value                          |
|------------------------------|--------------------------------------------------|
| `GEMINI_API_KEY`             | Local `.env`                                     |
| `FISH_AUDIO_API_KEY`         | Local `.env`                                     |
| `CF_ACCOUNT_ID`              | Local `.env`                                     |
| `CF_API_TOKEN`               | Local `.env`                                     |
| `YOUTUBE_CLIENT_ID`          | Local `.env`                                     |
| `YOUTUBE_CLIENT_SECRET`      | Local `.env`                                     |
| `YOUTUBE_REFRESH_TOKEN`      | Local `.env`                                     |
| `YOUTUBE_CHANNEL_ID`         | `UC7RIXToEFJrQOKjI0tAdZeA` (the AI Dollar id)    |
| `MAKE_INSTAGRAM_WEBHOOK_URL` | Local `.env`                                     |
| `INSTAGRAM_USERNAME`         | `theaidollar1741`                                |
| `PEXELS_API_KEY`             | Local `.env` (optional; used as a fallback only) |

`GITHUB_TOKEN` is provided automatically — do NOT create one for it.

## 2. Verify the workflow

Repo → **Actions** tab. The workflow is `Daily post`. If secrets are set it
turns green with a green run button.

## 3. First real run

- Open the workflow → **Run workflow**.
- Leave both inputs at `true` for a full YouTube + Instagram post, or set
  `youtube` to `false` for a caption-only Instagram test.
- Runs take 5–8 min. Watch the `Run one post` step for the pipeline log.

Success looks like:
- The workflow ends green.
- A new Release appears under **Releases** with a `video.mp4` asset.
- YouTube Studio shows a new upload.
- Instagram shows a new Reel within a minute or two (Make.com fetches the
  Release URL and pushes to Instagram).

## 4. After the first successful run

- The two cron jobs (`30 15 * * *` and `0 20 * * *`) will fire on schedule.
- The Render web service is no longer needed for posting. Options:
  - Leave it running — no harm; it just idles.
  - Suspend it in the Render dashboard.
- Any push to the repo counts as activity, so GitHub will not disable the
  scheduled workflow. If the repo goes quiet for 60 days it stops the
  schedule automatically; a `git commit --allow-empty -m "keep alive"`
  push resumes it.

## 5. Rolling back

The old Render-based path still works. Delete or disable the workflow file
and Render's own scheduler runs the same code as before. `main.py` runs
in the old long-lived mode when invoked without `--post-once`.
