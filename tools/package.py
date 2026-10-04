#!/usr/bin/env python3
"""Build an episode's upload package from meta.json "package" + FACTSHEET sources + the photo credits actually used.

  package.py <slug> <ID>

Reads  episodes/<dir>/meta.json "package":
  {"titles": [main, alt...], "summary": "...", "cta": "...", "tags": [...], "chapter_names": {"COLD OPEN": "Intro"},
   "notes": "accuracy caveats", "thumbnail": "A",
   "shorts": [{"role": "short1", "title": "... #shorts", "hook": "...", "social": "...", "sources": "...", "tags": [...]}, ...]}
Expects renders in out/: long.mp4, short1.mp4, short2.mp4, thumb_<X>.jpg.
Writes out/publish.json (for publish/publish.py) and out/Upload Details.html (human copy of everything).
Credits: assets/web/CREDITS.md lines "- <key>: File:<name> | <author> | <licence> | <url>"; a key counts as used when the
episode source references web/<key>.<ext>, or cut/<name>.png (made from web/p_<name>).
"""
import html, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from forge import channel, channel_dir  # noqa: E402
from ep import find  # noqa: E402

LEAD = 0.4


def used_keys(src_dir):
    code = "".join(open(os.path.join(src_dir, f)).read() for f in os.listdir(src_dir) if f.endswith((".ts", ".tsx")))
    return set(re.findall(r'web/(\w+)\.\w+', code)) | {"p_" + k for k in re.findall(r'cut/(\w+)\.png', code)}


def credits(ep_dir, src_dir):
    p = os.path.join(ep_dir, "assets/web/CREDITS.md")
    rows = {}
    if os.path.exists(p):
        for line in open(p):
            if line.startswith("- ") and ":" in line:
                k, rest = line[2:].split(":", 1)
                parts = [x.strip() for x in rest.split("|")]
                if len(parts) >= 4:
                    rows[k.strip()] = (parts[0].replace("File:", ""), parts[1], parts[2], parts[3])
    use = used_keys(src_dir)
    return [(k,) + v for k, v in sorted(rows.items()) if k in use]


def chapters(ep_dir, names):
    out = []
    for x in json.load(open(os.path.join(ep_dir, "audio/sections_tight.json"))):
        t = 0 if not out else x["s"] + LEAD
        n = names.get(x["name"]) or re.sub(r"^CHAPTER (\d+):\s*", r"\1. ", x["name"]).title()
        m, s = divmod(int(t), 60)
        out.append(f"{m}:{s:02d} {n}")
    return out if len(out) >= 3 else []


def sources(ep_dir):
    t = open(os.path.join(ep_dir, "FACTSHEET.md")).read()
    if "## Sources" not in t:
        return []
    return [l[2:].strip() for l in re.split(r"\n## ", t.split("## Sources", 1)[1])[0].splitlines() if l.startswith("- ")]


def main():
    slug, eid = sys.argv[1], sys.argv[2]
    c, m = channel(slug), find(slug, eid)
    d, pk = m["_dir"], m.get("package")
    if not pk:
        sys.exit("meta.json has no package section")
    src = os.path.join(channel_dir(slug), "studio/src/episodes", eid)
    cr = credits(d, src)
    who = sorted({f"- {w} ({lic})" for _, _, w, lic, _ in cr if w.lower() not in ("", "unknown")})
    yt = c.get("youtube", {})
    footer = yt.get("description_footer") or f"Subscribe to {c['name']} for the next one."
    desc = "\n\n".join(x for x in [
        pk["summary"], "\n".join(chapters(d, pk.get("chapter_names", {}))), pk.get("cta", ""), footer,
        "SOURCES\n" + "\n".join(f"- {s}" for s in sources(d)) if sources(d) else "",
        pk.get("notes", ""),
        "PHOTO CREDITS (Wikimedia Commons, free licences; cut-outs and grading by " + c["name"] + ")\n" + "\n".join(who) if who else "",
    ] if x)
    if len(desc) > 5000:
        sys.exit(f"description is {len(desc)} chars (YouTube max 5000): shorten summary/sources")
    tags, lang, cat = pk.get("tags", []), yt.get("language", "en"), yt.get("category_id", 24)
    items = [{"key": "long", "role": "long", "file": "long.mp4", "title": pk["titles"][0], "description": desc, "tags": tags,
              "thumbnail": f"thumb_{pk.get('thumbnail', 'A')}.jpg", "categoryId": cat, "lang": lang}]
    tagline = " ".join(f"#{t}" for t in c.get("hashtags", []))
    for sh in pk.get("shorts", []):
        sd = (f"{sh['hook']}\n\nFull video on our channel: {pk['titles'][0]}\n"
              + (f"Sources: {sh['sources']}\n" if sh.get("sources") else "")
              + ("\nPhotos via Wikimedia Commons (free licences):\n" + "\n".join(who) + "\n" if who else "") + f"\n#shorts {tagline}").strip()
        social = f"{sh.get('social', sh['hook'])}\n\nThe full story is on the {c['name']} YouTube channel.\n\n{tagline}".strip()
        items.append({"key": sh["role"], "role": sh["role"], "file": f"{sh['role']}.mp4", "title": sh["title"][:100], "description": sd[:5000],
                      "tags": sh.get("tags", tags[:6]), "categoryId": cat, "lang": lang, "social": social[:2200]})
    out = os.path.join(d, "out")
    for it in items:
        for f in (it["file"], it.get("thumbnail")):
            if f and not os.path.exists(os.path.join(out, f)):
                sys.exit(f"missing render out/{f}")
    full = "\n".join(f"{k}: {f} by {w}, {lic}, {u}" for k, f, w, lic, u in cr)
    man = {"channel_slug": slug, "channel": yt.get("channel_title") or c["name"], "episode": eid, "youtube": items,
           "credits_comment": f"Photo credits (Wikimedia Commons):\n{full}" if cr else ""}
    old = os.path.join(out, "publish.json")
    if os.path.exists(old):  # keep booked times when re-packaging
        prev = {i["key"]: i.get("publishAt") for i in json.load(open(old))["youtube"]}
        for it in items:
            if prev.get(it["key"]):
                it["publishAt"] = prev[it["key"]]
    json.dump(man, open(old, "w"), indent=1, ensure_ascii=False)
    e = html.escape
    page = (f"<html><head><meta charset='utf-8'><title>{eid} upload details</title></head><body style='font-family:Helvetica;max-width:900px'>"
            f"<h1>{eid}: {e(pk['titles'][0])}</h1><h2>Titles</h2><ol>{''.join(f'<li>{e(t)}</li>' for t in pk['titles'])}</ol>"
            f"<h2>Description ({len(desc)} chars)</h2><pre style='white-space:pre-wrap'>{e(desc)}</pre><h2>Tags</h2><p>{e(', '.join(tags))}</p>"
            + "".join(f"<h2>{e(i['role'])}: {e(i['title'])}</h2><pre style='white-space:pre-wrap'>{e(i['description'])}</pre>"
                      f"<h3>Facebook/Instagram caption</h3><pre style='white-space:pre-wrap'>{e(i.get('social', ''))}</pre>" for i in items[1:])
            + f"<h2>Photo credits</h2><pre style='white-space:pre-wrap'>{e(full)}</pre></body></html>")
    open(os.path.join(out, "Upload Details.html"), "w").write(page)
    print(f"publish.json: {len(items)} videos, description {len(desc)} chars, {len(cr)} credits")


if __name__ == "__main__":
    main()
