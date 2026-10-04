#!/usr/bin/env python3
"""Create a channel workspace: <FORGE_HOME>/<slug>/ with channel.json, brand/, episodes/, and a Remotion studio.

  new_channel.py <slug> --name "Channel Name" --code LF [--source <youtube url>]
  new_channel.py brand <slug>      regenerate studio/src/brand/brand.ts from channel.json "brand" and copy logos into every episode

The studio shares one node_modules install (<FORGE_HOME>/.deps) across channels to save disk.
"""
import argparse, datetime as dt, json, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from forge import HOME, PLUGIN  # noqa: E402

TEMPLATE = os.path.join(PLUGIN, "studio-template")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,40}$")


def deps():
    """One shared node_modules for every channel studio."""
    d = os.path.join(HOME, ".deps")
    if not os.path.isdir(os.path.join(d, "node_modules", "remotion")):
        os.makedirs(d, exist_ok=True)
        shutil.copy(os.path.join(TEMPLATE, "package.json"), d)
        print("installing Remotion (one time, ~300 MB)...")
        subprocess.run(["npm", "install", "--no-audit", "--no-fund", "--loglevel=error"], cwd=d, check=True)
    return os.path.join(d, "node_modules")


FONT_DEFAULT = {"serif": "Bodoni Moda", "sans": "Inter", "cond": "Anton", "type": "Courier Prime"}
COLOR_DEFAULT = {"deep": "#030F20", "navy": "#041B38", "navy2": "#123258", "gold": "#E9A82C", "gold2": "#F6CB62", "goldDeep": "#BE8617",
                 "ivory": "#F8F3E8", "paper": "#EFE7D6", "red": "#D7263D", "green": "#2BB673", "dim": "#9AA6BD"}
WEIGHTS = {"serif": ["500", "700", "900"], "sans": ["500", "700", "800", "900"], "cond": ["400"], "type": ["400", "700"]}


def font_module(family, studio):
    name = re.sub(r"[^A-Za-z0-9]", "", family)
    if not os.path.exists(os.path.join(studio, "node_modules/@remotion/google-fonts/dist/esm", name + ".mjs")):
        sys.exit(f"'{family}' is not a Google Font Remotion knows (looked for @remotion/google-fonts/{name})")
    return name


def brand_ts(c, studio):
    b = c["brand"]
    colors = {**COLOR_DEFAULT, **b.get("colors", {})}
    fonts = {**FONT_DEFAULT, **b.get("fonts", {})}
    for k, v in colors.items():
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", v):
            sys.exit(f"brand colour {k}={v!r} must be #RRGGBB")
    q = lambda v: json.dumps(v, ensure_ascii=False)
    imports = "".join(f'import * as {k}F from "@remotion/google-fonts/{font_module(fam, studio)}";\n' for k, fam in fonts.items())
    col = ",\n    ".join(f"{k}: {q(v)}" for k, v in colors.items())
    fnt = (f'serif: gfont(serifF, {q(WEIGHTS["serif"])}), serifI: gfont(serifF, ["500", "700"], "italic"),\n    '
           f'sans: gfont(sansF, {q(WEIGHTS["sans"])}), cond: gfont(condF, {q(WEIGHTS["cond"])}), type: gfont(typeF, {q(WEIGHTS["type"])})')
    return (imports + 'import { gfont } from "../kit/fonts";\n\n'
            f"// Generated from channel.json by `new_channel.py brand {c['slug']}`. Edit channel.json brand, not this file.\n"
            "// Colour roles: deep/navy/navy2 = background ramp, gold/gold2/goldDeep = accent ramp (any hue), ivory = main text,\n"
            "// paper = document cards, red = negative stamps, green = positive verdicts, dim = secondary text.\n"
            f"export const BRAND = {{\n  name: {q(c['name'])},\n  handle: {q(c.get('handle', ''))},\n  tagline: {q(c.get('tagline', ''))},\n"
            '  wordmark: "brand/wordmark.png",\n  mono: "brand/mono.png",\n'
            f"  colors: {{\n    {col},\n  }},\n  fonts: {{\n    {fnt},\n  }},\n}};\n")


def sync_brand(slug):
    root = os.path.join(HOME, slug)
    c = json.load(open(os.path.join(root, "channel.json")))
    open(os.path.join(root, "studio/src/brand/brand.ts"), "w").write(brand_ts(c, os.path.join(root, "studio")))
    n = 0
    for ep in sorted(os.listdir(os.path.join(root, "episodes"))):
        dst = os.path.join(root, "episodes", ep, "assets", "brand")
        if os.path.isdir(os.path.dirname(dst)):
            os.makedirs(dst, exist_ok=True)
            for f in ("wordmark.png", "mono.png"):
                p = os.path.join(root, "brand", f)
                if os.path.exists(p):
                    shutil.copy(p, dst); n += 1
    print(f"brand.ts written; {n} logo files copied into episodes")


def create(a):
    if not SLUG.match(a.slug):
        sys.exit("slug must be lowercase letters, digits and dashes (2-41 chars)")
    if not re.fullmatch(r"[A-Z]{2,4}", a.code):
        sys.exit("--code must be 2-4 capital letters (episode ids become CODE01, CODE02...)")
    root = os.path.join(HOME, a.slug)
    if os.path.exists(root):
        sys.exit(f"{root} already exists")
    for d in ("brand", "episodes", "audit", "studio"):
        os.makedirs(os.path.join(root, d))
    st = os.path.join(root, "studio")
    shutil.copytree(os.path.join(TEMPLATE, "src"), os.path.join(st, "src"), ignore=shutil.ignore_patterns("_demo"))
    for f in ("package.json", "tsconfig.json"):
        shutil.copy(os.path.join(TEMPLATE, f), st)
    idx = os.path.join(st, "src/episodes/index.ts")
    s = open(idx).read().replace('import demo from "./_demo";\n', "").replace("EPISODES: EpisodeEntry[] = [demo];", "EPISODES: EpisodeEntry[] = [\n];")
    open(idx, "w").write(s)
    os.symlink(deps(), os.path.join(st, "node_modules"))
    c = json.load(open(os.path.join(PLUGIN, "templates", "channel.json")))
    c.update({"slug": a.slug, "name": a.name, "code": a.code, "created": dt.date.today().isoformat()})
    c["source"]["url"] = a.source or ""
    c["brand"] = {"colors": dict(COLOR_DEFAULT), "fonts": dict(FONT_DEFAULT)}
    json.dump(c, open(os.path.join(root, "channel.json"), "w"), indent=1, ensure_ascii=False)
    open(os.path.join(st, "src/brand/brand.ts"), "w").write(brand_ts(c, st))
    print(root)


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "brand":
        return sync_brand(sys.argv[2])
    ap = argparse.ArgumentParser()
    ap.add_argument("slug"); ap.add_argument("--name", required=True); ap.add_argument("--code", required=True); ap.add_argument("--source")
    create(ap.parse_args())


if __name__ == "__main__":
    main()
