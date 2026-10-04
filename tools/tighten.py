#!/usr/bin/env python3
"""Cap pauses in audio/vo.mp3 and speed it up; remap word (and section) timestamps to match.
Writes audio/vo_tight.wav, audio/words_tight.json, audio/sections_tight.json.

  tighten.py <episode dir> [tempo]     tempo 1.0-1.15 sounds natural; pick it to hit the target words-per-minute."""
import json, subprocess, sys, pathlib
ROOT = pathlib.Path(sys.argv[1]).resolve()
CAP, TEMPO = 0.32, float(sys.argv[2]) if len(sys.argv) > 2 else 1.1
w = json.load(open(ROOT / "audio/words.json"))
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ROOT / "audio/vo.mp3")]))
# keep-intervals: speech plus capped gaps, cut in the middle of each long gap
keep, a = [], max(0.0, w[0]["s"] - 0.05)
for i in range(len(w) - 1):
    g0, g1 = w[i]["e"], w[i + 1]["s"]
    if g1 - g0 > CAP:
        keep.append((a, g0 + CAP / 2)); a = g1 - CAP / 2
keep.append((a, min(dur, w[-1]["e"] + 0.4)))
def remap(t):
    out = 0.0
    for s, e in keep:
        if t <= e: return (out + max(0.0, t - s)) / TEMPO
        out += e - s
    return out / TEMPO
json.dump([{"w": x["w"], "s": round(remap(x["s"]), 3), "e": round(remap(x["e"]), 3)} for x in w], open(ROOT / "audio/words_tight.json", "w"))
sm = ROOT / "audio/sections.json"
if sm.exists():
    json.dump([{**x, "s": round(remap(x["s"]), 3), "e": round(remap(x["e"]), 3)} for x in json.load(open(sm))], open(ROOT / "audio/sections_tight.json", "w"), indent=1)
parts = "".join(f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS[p{i}];" for i, (s, e) in enumerate(keep))
fc = parts + "".join(f"[p{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=0:a=1,atempo={TEMPO}[out]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / "audio/vo.mp3"), "-filter_complex", fc, "-map", "[out]", "-ar", "48000", str(ROOT / "audio/vo_tight.wav")], check=True)
print(f"{len(keep)} segments; new length {sum(e - s for s, e in keep) / TEMPO:.1f}s")
