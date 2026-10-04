#!/usr/bin/env python3
"""Wikimedia Commons helper.
  search:  commons.py search "<query>" [n]           -> list File: titles with size + license
  fetch:   commons.py fetch <outdir> <key> "<File:Title>" [width]
           downloads a rendered copy (SVG -> PNG) and appends attribution to <outdir>/CREDITS.md
"""
import json, os, re, sys, urllib.parse, urllib.request

API = "https://en.wikipedia.org/w/api.php"  # commons.wikimedia.org is unreachable here; enwiki serves Commons files too
UA = {"User-Agent": "Shadowcast/1.0 (contact via commons talk page)"}

def get(url, timeout=60):
    import time
    for i in range(6):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == 5: raise
            time.sleep(15 * (i + 1))

def call(params):
    q = urllib.parse.urlencode({**params, "format": "json"})
    return json.loads(get(f"{API}?{q}"))

def meta(ii):
    m = ii.get("extmetadata", {})
    g = lambda k: re.sub(r"<[^>]+>", "", m.get(k, {}).get("value", "")).strip()
    return g("LicenseShortName"), g("Artist")[:80]

def search(query, n=6):
    r = call({"action": "query", "generator": "search", "gsrnamespace": 6, "gsrsearch": query, "gsrlimit": n,
              "prop": "imageinfo", "iiprop": "size|extmetadata"})
    pages = sorted(r.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0))
    for p in pages:
        ii = p["imageinfo"][0]; lic, art = meta(ii)
        print(f'{ii["width"]}x{ii["height"]} | {lic} | {art} | {p["title"]}')

def fetch(outdir, key, title, width=1920):
    r = call({"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": width})
    p = next(iter(r["query"]["pages"].values())); ii = p["imageinfo"][0]
    url = ii.get("thumburl") or ii["url"]
    ext = ".png" if ii["mime"] in ("image/svg+xml", "image/png") else ".jpg"
    os.makedirs(outdir, exist_ok=True); path = os.path.join(outdir, key + ext)
    data = get(url, 120)
    with open(path, "wb") as fh:
        fh.write(data)
    lic, art = meta(ii)
    with open(os.path.join(outdir, "CREDITS.md"), "a") as fh:
        fh.write(f"- {key}: {title} | {art or 'unknown'} | {lic} | {ii['descriptionurl']}\n")
    print("saved", path, lic)

def lead(titles):
    r = call({"action": "query", "titles": "|".join(titles), "prop": "pageimages", "piprop": "name", "redirects": 1})
    for p in r["query"]["pages"].values():
        print(p["title"], "->", ("File:" + p["pageimage"]) if p.get("pageimage") else None)

if __name__ == "__main__":
    if sys.argv[1] == "lead": lead(sys.argv[2:])
    elif sys.argv[1] == "search": search(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 6)
    else: fetch(sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]) if len(sys.argv) > 5 else 1920)
