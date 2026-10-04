#!/usr/bin/env python3
"""Render brand/wordmark.png (trimmed, transparent) and brand/mono.png (+ avatar.png 800px) from the channel's brand font.
Exact spelling every time; use this when an image model's lettering isn't letter-perfect.   wordmark.py <slug>"""
import os, shutil, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import channel_dir  # noqa: E402
from PIL import Image  # noqa: E402

root = channel_dir(sys.argv[1]); studio = os.path.join(root, "studio"); brand = os.path.join(root, "brand")
os.makedirs(brand, exist_ok=True)
tmp = tempfile.mkdtemp()
for comp, out in (("BrandWordmark", "wordmark.png"), ("BrandMono", "mono.png")):
    p = os.path.join(tmp, out)
    r = subprocess.run(["npx.cmd" if os.name == "nt" else "npx", "remotion", "still", "src/index.ts", comp, p, f"--public-dir={tmp}", "--image-format=png", "--log=error"],
                       cwd=studio, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"render {comp} failed: {r.stderr[-600:]}")
    im = Image.open(p).convert("RGBA")
    if comp == "BrandWordmark":
        bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        im = im.crop((max(0, bb[0] - 24), max(0, bb[1] - 16), min(im.width, bb[2] + 24), min(im.height, bb[3] + 16)))
    im.save(os.path.join(brand, out))
Image.open(os.path.join(brand, "mono.png")).resize((800, 800), Image.LANCZOS).save(os.path.join(brand, "avatar.png"))
shutil.rmtree(tmp)
print("wrote", ", ".join(os.path.join(brand, f) for f in ("wordmark.png", "mono.png", "avatar.png")))
