#!/usr/bin/env python3
"""Render an episode (or one composition) and master the audio to -14 LUFS (YouTube level). macOS, Windows, Linux.

  render.py episode <slug> <ID> [long] [shorts] [thumbs]     -> episodes/<dir>/out/long.mp4, short1/2.mp4, thumb_A/B/C.jpg
  render.py comp <studio dir> <composition> <episode dir> <out.mp4> [--concurrency N]
Long videos render at concurrency 4; Shorts at 2 (they can eat several GB of memory).
SHADOWCAST_MIN_FREE_GB (default 3) guards against filling the disk mid-render.
"""
import json, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import channel_dir  # noqa: E402

NPX = "npx.cmd" if os.name == "nt" else "npx"


def need_disk(path):
    free = shutil.disk_usage(path).free / 1e9
    if free < float(os.environ.get("SHADOWCAST_MIN_FREE_GB", 3)):
        sys.exit(f"only {free:.1f} GB free; a render needs ~3 GB of temp space")


def loudnorm(raw, out):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-vn", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    d = json.loads(m.group(0)) if m else {"input_i": "-inf"}
    if d["input_i"] in ("-inf", "inf"):  # silent track (test renders): nothing to normalise
        af = []
    else:
        af = ["-af", (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:"
                      f"measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true,alimiter=limit=0.75:attack=2:release=60:level=false")]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-c:v", "copy", *af, "-ar", "48000", "-c:a", "aac", "-b:a", "192k", out], check=True)


def comp(studio, cid, ep, out, conc=4):
    need_disk(ep)
    raw = out[:-4] + ".raw.mp4"
    subprocess.run([NPX, "remotion", "render", "src/index.ts", cid, raw, f"--public-dir={ep}", "--codec=h264", "--crf=20",
                    f"--concurrency={conc}", "--log=error"], cwd=studio)
    if not os.path.exists(raw):
        sys.exit(f"render failed: {cid}")
    loudnorm(raw, out)
    os.remove(raw)
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "compact", out], capture_output=True, text=True)
    print(os.path.basename(out), p.stdout.strip())


def episode(slug, eid, what):
    from ep import find
    studio = os.path.join(channel_dir(slug), "studio")
    ep = find(slug, eid)["_dir"]
    out = os.path.join(ep, "out"); os.makedirs(out, exist_ok=True)
    r = subprocess.run([NPX, "remotion", "compositions", "src/index.ts", f"--public-dir={ep}", "--quiet"], cwd=studio, capture_output=True, text=True)
    comps = set(r.stdout.split())
    if eid not in comps:
        sys.exit(f"composition {eid} not found (registered? `ep.py register`). Remotion said: {r.stderr[-400:]}")
    if "long" in what:
        comp(studio, eid, ep, os.path.join(out, "long.mp4"), 4)
    if "shorts" in what:
        for k in (1, 2):
            if f"{eid}Short{k}" in comps:
                comp(studio, f"{eid}Short{k}", ep, os.path.join(out, f"short{k}.mp4"), 2)
    if "thumbs" in what:
        from PIL import Image
        for x in "ABC":
            if f"{eid}Thumb{x}" in comps:
                png = os.path.join(out, f"thumb_{x}.png")
                subprocess.run([NPX, "remotion", "still", "src/index.ts", f"{eid}Thumb{x}", png, f"--public-dir={ep}", "--log=error"], cwd=studio, check=True)
                Image.open(png).convert("RGB").save(png[:-4] + ".jpg", quality=90); os.remove(png)
                print(f"thumb_{x}.jpg")
    print("output:", out)


def main():
    a = sys.argv[1:]
    if len(a) >= 3 and a[0] == "episode":
        episode(a[1], a[2], set(a[3:]) or {"long", "shorts", "thumbs"})
    elif len(a) >= 5 and a[0] == "comp":
        conc = int(a[a.index("--concurrency") + 1]) if "--concurrency" in a else 4
        comp(os.path.abspath(a[1]), a[2], os.path.abspath(a[3]), os.path.abspath(a[4]), conc)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
