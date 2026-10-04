#!/usr/bin/env python3
"""Tile rendered stills into labelled contact sheets: sheet.py <dir> [cols] [per_sheet]"""
import sys, glob, os
from PIL import Image, ImageDraw
d = sys.argv[1]; cols = int(sys.argv[2]) if len(sys.argv) > 2 else 5; per = int(sys.argv[3]) if len(sys.argv) > 3 else 25
files = sorted(glob.glob(os.path.join(d, "f*.jpg")))
for s in range(0, len(files), per):
    chunk = files[s:s + per]; tw, th = 384, 216; rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), "black"); dr = ImageDraw.Draw(sheet)
    for i, f in enumerate(chunk):
        im = Image.open(f).resize((tw, th)); x, y = (i % cols) * tw, (i // cols) * th; sheet.paste(im, (x, y))
        fr = int(os.path.basename(f)[1:6]); dr.rectangle([x, y, x + 110, y + 22], fill="black"); dr.text((x + 4, y + 4), f"{fr // 30 // 60}:{fr // 30 % 60:02d} f{fr}", fill="yellow")
    sheet.save(os.path.join(d, f"sheet{s // per}.jpg"), quality=85)
print("sheets:", (len(files) + per - 1) // per)
