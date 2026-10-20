# -*- coding: utf-8 -*-
"""Downscale portraits for embedding.

The originals are 1080x1920 PNG (~1 MB each). For a single-file game we want
roughly 320px wide WebP/JPEG, which is plenty for a card-sized display and
keeps the total payload small.
"""
import io
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "art-raw")
OUT = os.path.join(HERE, "art-web")
os.makedirs(OUT, exist_ok=True)

TARGET_W = 340
QUALITY = 78

names = sorted(f[:-4] for f in os.listdir(RAW) if f.lower().endswith(".png"))
report = []
total = 0

for name in names:
    src = os.path.join(RAW, name + ".png")
    im = Image.open(src)
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA")

    w, h = im.size
    if w > TARGET_W:
        nh = int(round(h * TARGET_W / float(w)))
        im = im.resize((TARGET_W, nh), Image.LANCZOS)

    # JPEG cannot hold alpha; portraits are opaque, so flatten onto the page bg
    has_alpha = im.mode == "RGBA"
    if has_alpha:
        # keep alpha only if the image actually uses it
        alpha = im.getchannel("A")
        if alpha.getextrema()[0] >= 250:
            im = im.convert("RGB")
            has_alpha = False

    if has_alpha:
        dest = os.path.join(OUT, name + ".webp")
        im.save(dest, "WEBP", quality=QUALITY, method=6)
    else:
        dest = os.path.join(OUT, name + ".jpg")
        im.convert("RGB").save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)

    size = os.path.getsize(dest)
    total += size
    report.append({"name": name, "file": os.path.basename(dest), "bytes": size,
                   "w": im.size[0], "h": im.size[1]})
    print("%-8s %4dx%-4d %6.1f KB  %s" % (name, im.size[0], im.size[1], size / 1024.0,
                                          os.path.basename(dest)))

print("\n共 %d 张，合计 %.2f MB" % (len(report), total / 1024.0 / 1024.0))
with io.open(os.path.join(HERE, "art-manifest.json"), "w", encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=2)
