"""Render the same subjects through each candidate image model and write a
side-by-side contact sheet, so image quality can be judged before a video is
built rather than after an upload.

Usage:  python tools/image_bakeoff.py
Needs CF_ACCOUNT_ID and CF_API_TOKEN in the environment or .env.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import video_generator as vg  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

# Subjects picked to cover the range the curriculum actually produces: a
# still object, a chart, a scene with hands, and a building.
SUBJECTS = [
    "a cash register drawer open and overflowing with hundred dollar bills",
    "a stack of gold coins beside a rising green bar chart",
    "hands signing a mortgage contract with house keys on the desk",
    "a modern glass bank headquarters at dusk",
]

MODELS = [
    "@cf/stabilityai/stable-diffusion-xl-base-1.0",
    "@cf/black-forest-labs/flux-1-schnell",
]

TILE_W, TILE_H = 300, 533   # 9:16 thumbnails for the sheet
LABEL_H = 26


def main():
    if not (vg.CF_ACCOUNT_ID and vg.CF_API_TOKEN):
        print("CF_ACCOUNT_ID / CF_API_TOKEN are not set — nothing to test.")
        return 1

    out_dir = os.path.join(os.environ.get("TMP", "."), "image_bakeoff")
    os.makedirs(out_dir, exist_ok=True)

    grid = {}
    for model in MODELS:
        vg.CF_IMAGE_MODEL = model
        short = model.rsplit("/", 1)[-1]
        for si, subject in enumerate(SUBJECTS):
            path = os.path.join(out_dir, f"{short}_{si}.jpg")
            t0 = time.time()
            ok = vg.generate_image(subject, path, seed=si * 101 + 5)
            print(f"{short:<28} #{si} {'ok' if ok else 'FAILED'} "
                  f"{time.time() - t0:5.1f}s")
            grid[(model, si)] = path if ok else None

    sheet = Image.new("RGB",
                      (TILE_W * len(SUBJECTS), (TILE_H + LABEL_H) * len(MODELS)),
                      (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    for mi, model in enumerate(MODELS):
        y = mi * (TILE_H + LABEL_H)
        draw.text((6, y + 7), model.rsplit("/", 1)[-1], fill=(255, 255, 255))
        for si in range(len(SUBJECTS)):
            p = grid.get((model, si))
            if p and os.path.exists(p):
                tile = Image.open(p).convert("RGB").resize((TILE_W, TILE_H))
                sheet.paste(tile, (si * TILE_W, y + LABEL_H))

    sheet_path = os.path.join(out_dir, "bakeoff_sheet.png")
    sheet.save(sheet_path)
    print("\nSHEET:", sheet_path)
    print("Full-size renders in:", out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
