#!/usr/bin/env python3
"""Pull brand inputs from a website, a folder of brand files, or reference images.

  brand_extract.py site <https://example.com> <out dir>   name, tagline, logo/icon files, colours, fonts -> <out>/brand_source.json
  brand_extract.py folder <dir> <out dir>                 the user's own logo/brand files -> colours from the logo + font names found
  brand_extract.py palette <img> [img...]                 dominant colours of images (e.g. the audit's thumbs.jpg / frames)

Output colours are suggestions mapped onto the kit's roles (deep/navy/navy2 background ramp, gold/gold2/goldDeep accent
ramp, ivory text); the brand-kit skill reviews them before writing channel.json.
"""
import colorsys, json, os, re, shutil, sys, urllib.parse
from collections import Counter
from html.parser import HTMLParser

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/128 Safari/537.36"}
MAX = 3_000_000
IMG = (".png", ".jpg", ".jpeg", ".webp", ".svg", ".ico")


def get(url, binary=False):
    import requests
    if not re.match(r"^https?://", url):
        raise ValueError("only http(s) URLs")
    r = requests.get(url, headers=UA, timeout=30, stream=True)
    r.raise_for_status()
    data = r.raw.read(MAX, decode_content=True)
    return data if binary else data.decode(r.encoding or "utf-8", errors="ignore")


# ---------- colour helpers ----------
def hexc(rgb):
    return "#%02X%02X%02X" % tuple(int(max(0, min(255, c))) for c in rgb)


def rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hls(c):
    return colorsys.rgb_to_hls(*(x / 255 for x in c))


def shade(c, l):
    h, _, s = hls(c)
    return tuple(round(x * 255) for x in colorsys.hls_to_rgb(h, l, s))


def image_colors(paths, k=8):
    """Dominant colours (k-means on a downsample), most common first."""
    import numpy as np
    from PIL import Image
    px = []
    for p in paths:
        try:
            im = Image.open(p).convert("RGBA"); im.thumbnail((160, 160))
            a = np.asarray(im).reshape(-1, 4)
            px.append(a[a[:, 3] > 200][:, :3])  # ignore transparent pixels (logos)
        except Exception:
            continue
    if not px:
        return []
    X = np.concatenate(px).astype(float)
    rng = np.random.default_rng(0)
    C = X[rng.choice(len(X), size=min(k, len(X)), replace=False)]
    for _ in range(15):
        lab = ((X[:, None] - C[None]) ** 2).sum(-1).argmin(1)
        C = np.array([X[lab == i].mean(0) if (lab == i).any() else C[i] for i in range(len(C))])
    counts = np.bincount(lab, minlength=len(C))
    return [(hexc(C[i]), int(counts[i])) for i in counts.argsort()[::-1]]


def roles(colors):
    """Map a list of hex colours (most important first) onto the kit's colour roles."""
    cs = [rgb(c) for c in colors]
    if not cs:
        return {}
    dark = sorted(cs, key=lambda c: hls(c)[1])[0]
    vivid = [c for c in cs if hls(c)[2] > 0.35 and 0.25 < hls(c)[1] < 0.8]
    accent = max(vivid[:5], key=lambda c: hls(c)[2]) if vivid else sorted(cs, key=lambda c: -hls(c)[2])[0]
    h, _, s = hls(dark)
    deep = dark if hls(dark)[1] < 0.12 else shade(dark, 0.07)
    return {"deep": hexc(deep), "navy": hexc(shade(deep, 0.12)), "navy2": hexc(shade(deep, 0.22)),
            "gold": hexc(accent), "gold2": hexc(shade(accent, min(0.85, hls(accent)[1] + 0.15))),
            "goldDeep": hexc(shade(accent, max(0.2, hls(accent)[1] - 0.15))), "ivory": "#F8F5EE", "dim": "#9AA3B5"}


# ---------- website ----------
class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta, self.links, self.imgs, self.styles, self.title, self._t, self._s = {}, [], [], [], "", False, False

    def handle_starttag(self, tag, a):
        a = {k: (v or "") for k, v in a}
        if tag == "meta":
            k = (a.get("property") or a.get("name") or "").lower()
            if k:
                self.meta[k] = a.get("content", "")
        elif tag == "link":
            self.links.append(a)
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "title":
            self._t = True
        elif tag == "style":
            self._s = True
        if a.get("style"):
            self.styles.append(a["style"])

    def handle_endtag(self, tag):
        self._t = self._t and tag != "title"
        self._s = self._s and tag != "style"

    def handle_data(self, d):
        if self._t:
            self.title += d
        if self._s:
            self.styles.append(d)


def site(url, out):
    os.makedirs(out, exist_ok=True)
    html = get(url)
    p = Head(); p.feed(html)
    css = "\n".join(p.styles)
    for l in p.links:
        if "stylesheet" in l.get("rel", "").lower() and l.get("href"):
            try:
                css += "\n" + get(urllib.parse.urljoin(url, l["href"]))[:MAX]
            except Exception:
                pass
    # colours: theme-color first, then CSS custom properties named like brand/primary/accent, then frequency
    found = []
    if re.match(r"#[0-9a-fA-F]{3,6}$", p.meta.get("theme-color", "")):
        found.append(p.meta["theme-color"])
    named = re.findall(r"--[\w-]*(?:brand|primary|accent|main|secondary)[\w-]*\s*:\s*(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})\b", css)
    freq = Counter(c.upper() for c in re.findall(r"#[0-9a-fA-F]{6}\b", css))
    greys = lambda c: hls(rgb(c))[2] < 0.08
    found += named + [c for c, _ in freq.most_common(40) if not greys(c)][:8] + [c for c, _ in freq.most_common(40) if greys(c)][:3]
    colors = list(dict.fromkeys(c.upper() if len(c) == 7 else c for c in found))[:12]
    # fonts: Google Fonts links + font-family declarations
    fonts = []
    for l in p.links:
        for fam in re.findall(r"family=([^&:]+)", urllib.parse.unquote(l.get("href", ""))):
            fonts.append(fam.replace("+", " "))
    for fam in re.findall(r"font-family\s*:\s*([^;}{]+)", css):
        first = fam.split(",")[0].strip().strip("'\"")
        if first and not first.startswith("var(") and first.lower() not in ("inherit", "initial", "sans-serif", "serif", "monospace", "system-ui", "-apple-system"):
            fonts.append(first)
    fonts = [f for f, _ in Counter(fonts).most_common(6)]
    # logo candidates: <img> with "logo" in src/alt/class, apple-touch-icon, icons, og:image
    cands = [i.get("src") for i in p.imgs if "logo" in (i.get("src", "") + i.get("alt", "") + i.get("class", "")).lower() and i.get("src")]
    cands += [l.get("href") for l in p.links if any(k in l.get("rel", "").lower() for k in ("apple-touch-icon", "icon")) and l.get("href")]
    if p.meta.get("og:image"):
        cands.append(p.meta["og:image"])
    files = []
    for i, c in enumerate(dict.fromkeys(cands)):
        u = urllib.parse.urljoin(url, c)
        ext = os.path.splitext(urllib.parse.urlparse(u).path)[1].lower()
        if ext not in IMG:
            ext = ".png"
        try:
            data = get(u, binary=True)
            if len(data) > 300:
                f = os.path.join(out, f"site_logo_{i}{ext}"); open(f, "wb").write(data); files.append(f)
        except Exception:
            continue
        if len(files) >= 5:
            break
    raster = [f for f in files if not f.endswith((".svg", ".ico"))]
    logo_cols = [c for c, _ in image_colors(raster[:2], k=5)] if raster else []
    name = p.meta.get("og:site_name") or re.split(r"\s+[|\-–—:]\s+", p.title.strip())[0]
    res = {"source": url, "name": name.strip(), "tagline": (p.meta.get("description") or p.meta.get("og:description") or "")[:200],
           "colors": colors, "logo_colors": logo_cols, "fonts": fonts, "logo_files": files,
           "suggested_roles": roles(colors or logo_cols)}
    json.dump(res, open(os.path.join(out, "brand_source.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(res, indent=1, ensure_ascii=False))


def folder(src, out):
    os.makedirs(out, exist_ok=True)
    files, fonts, notes = [], [], []
    for root, _, names in os.walk(src):
        for n in names:
            p = os.path.join(root, n); low = n.lower()
            if low.endswith(IMG):
                dst = os.path.join(out, "user_" + re.sub(r"[^\w.-]", "_", n)); shutil.copy(p, dst); files.append(dst)
            elif low.endswith((".ttf", ".otf", ".woff", ".woff2")):
                fonts.append(n)
            elif low.endswith((".txt", ".md", ".json")) and os.path.getsize(p) < 200_000:
                notes.append({"file": n, "text": open(p, errors="ignore").read()[:4000]})
    raster = [f for f in files if not f.endswith((".svg", ".ico"))]
    cols = [c for c, _ in image_colors(raster[:4], k=6)]
    res = {"source": src, "files": files, "font_files": fonts, "notes": notes, "colors_from_images": cols, "suggested_roles": roles(cols)}
    json.dump(res, open(os.path.join(out, "brand_source.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(res, indent=1, ensure_ascii=False))


def palette(paths):
    cols = image_colors(paths, k=8)
    print(json.dumps({"dominant": cols, "suggested_roles": roles([c for c, _ in cols])}, indent=1))


def main():
    a = sys.argv[1:]
    if len(a) == 3 and a[0] == "site":
        site(a[1], a[2])
    elif len(a) == 3 and a[0] == "folder":
        folder(os.path.expanduser(a[1]), a[2])
    elif len(a) >= 2 and a[0] == "palette":
        palette(a[1:])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
