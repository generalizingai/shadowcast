#!/usr/bin/env python3
"""Cut a person/subject out of a photo -> transparent PNG cropped to the subject with a small margin.

  cutout.py <in.jpg|png> <out.png>
macOS 14+: uses the Apple Vision tool (build once with build_cutout.sh; best quality, offline, free).
Windows/Linux (or no Vision tool): uses rembg (`python -m pip install "rembg[cpu]"`; downloads a ~170 MB model on first use).
"""
import os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CFG  # noqa: E402

VISION = os.path.join(CFG, "bin", "cutout")


def with_rembg(src, dst):
    try:
        from rembg import remove
    except ImportError:
        sys.exit('cut-out needs rembg on this system: python -m pip install "rembg[cpu]"')
    from PIL import Image
    im = remove(Image.open(src).convert("RGB"))
    bb = im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    if not bb:
        sys.exit("no subject found")
    m = int(0.02 * max(im.size))
    im.crop((max(0, bb[0] - m), max(0, bb[1] - m), min(im.width, bb[2] + m), min(im.height, bb[3] + m))).save(dst)
    print("ok (rembg)", im.size)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    if sys.platform == "darwin" and os.path.exists(VISION):
        r = subprocess.run([VISION, src, dst], capture_output=True, text=True)
        if r.returncode == 0:
            return print(r.stdout.strip())
        print(f"Vision cut-out failed ({r.stderr.strip()}); trying rembg", file=sys.stderr)
    with_rembg(src, dst)


if __name__ == "__main__":
    main()
