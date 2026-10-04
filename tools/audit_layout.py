#!/usr/bin/env python3
"""Busiest-frame layout audit: render the LAST frame of every shot (all its elements are on screen) for the long video
and each Short, then build review sheets. Review every sheet for overlaps, text touching or crossing a frame edge,
wrapped labels that shift charts, faces covered by text, and empty frames.

  audit_layout.py <studio dir> <episode dir> <EpisodeId> [src folder, default EpisodeId]
Conventions (episode skill): long shots live in src/episodes/<EpisodeId>/shots*.tsx; Shorts in short1.tsx / short2.tsx,
each containing `prefix="<section name prefix>"`. Writes <episode>/out/audit/{long_*.jpg, short1.jpg, short2.jpg}.
"""
import glob, json, os, re, shutil, subprocess, sys

FPS = 30
SHOT = re.compile(r'\{ at: "([^"]*)"(?:, sfx: "\w+")?(?:, marks: \[([^\]]*)\])?')


def norm(x):
    return re.sub(r"[^a-z0-9]", "", x.lower())


def starts(src, words, lead, base=0.0):
    n = [norm(w["w"]) for w in words]
    cur, out = 0, []
    for m in SHOT.finditer(src):
        phrases = [m.group(1)] + re.findall(r'"([^"]*)"', m.group(2) or "")
        first = None
        for k, p in enumerate(phrases):
            if p == "":
                t = -lead
            else:
                toks = [x for x in (norm(y) for y in p.split()) if x]
                i = next((i for i in range(cur, len(n)) if n[i:i + len(toks)] == toks), None)
                if i is None:
                    sys.exit(f"anchor not found: {p!r} (after word {cur}: {words[cur]['w'] if cur < len(words) else 'END'})")
                cur = i + 1; t = words[i]["s"] - base
            if k == 0:
                first = round((t + lead) * FPS)
        out.append(first)
    return out


def render(studio, comp, epdir, frames, outdir):
    os.makedirs(outdir, exist_ok=True)
    tool = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stills.mjs")
    r = subprocess.run(["node", tool, studio, comp, epdir, outdir, " ".join(map(str, frames))], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"render failed for {comp}: {r.stderr[-800:]}")


def sheets(indir, out_prefix, cols, w, h):
    from PIL import Image, ImageDraw
    fs = sorted(glob.glob(os.path.join(indir, "f*.jpg")))
    per = cols * 4
    made = []
    for s in range(0, len(fs), per):
        chunk = fs[s:s + per]; cols = min(cols, len(chunk)); rows = (len(chunk) + cols - 1) // cols
        c = Image.new("RGB", (cols * w, rows * h), (0, 0, 0))
        for i, f in enumerate(chunk):
            a = Image.open(f).resize((w, h)); d = ImageDraw.Draw(a); d.rectangle((0, h - 18, 70, h), fill="black"); d.text((3, h - 15), os.path.basename(f)[1:6], fill="yellow")  # bottom-left: keeps the corner bug visible
            c.paste(a, ((i % cols) * w, (i // cols) * h))
        p = f"{out_prefix}{s // per}.jpg"; c.save(p, quality=88); made.append(p)
    return made


def main():
    studio, ep, eid = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3]
    words = json.load(open(os.path.join(ep, "audio/words_tight.json")))
    secs = json.load(open(os.path.join(ep, "audio/sections_tight.json")))
    src_dir = os.path.join(studio, "src/episodes", sys.argv[4] if len(sys.argv) > 4 else eid)
    out = os.path.join(ep, "out/audit"); shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    tmp = os.path.join(out, "_frames")
    long_src = "".join(open(p).read() for p in sorted(glob.glob(os.path.join(src_dir, "shots*.tsx"))))
    total = int((words[-1]["e"] + 0.4 + 3) * FPS + 0.999)
    st = starts(long_src, words, 0.4)
    ends = [s - 4 for s in st[1:]] + [total - 4]
    render(studio, eid, ep, ends, tmp)
    made = sheets(tmp, os.path.join(out, "long_"), 3, 640, 360); shutil.rmtree(tmp)
    for k in (1, 2):
        p = os.path.join(src_dir, f"short{k}.tsx")
        if not os.path.exists(p):
            continue
        src = open(p).read()
        pre = re.search(r'prefix="([^"]+)"', src).group(1)
        sec = next(x for x in secs if x["name"].startswith(pre))
        sw = [w for w in words if sec["s"] - 0.01 <= w["s"] < sec["e"] + 0.01]
        st = starts(src, sw, 0.25, base=sec["s"])
        total = round((sec["e"] - sec["s"] + 0.25 + 0.3) * FPS)
        ends = [s - 4 for s in st[1:]] + [total - 4]
        render(studio, f"{eid}Short{k}", ep, ends, tmp)
        made += sheets(tmp, os.path.join(out, f"short{k}_"), 6, 270, 480); shutil.rmtree(tmp)
    print("\n".join(made))


if __name__ == "__main__":
    main()
