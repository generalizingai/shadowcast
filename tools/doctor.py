#!/usr/bin/env python3
"""Check everything shadowcast needs and print the fix for anything missing.  doctor.py [--json]"""
import importlib, json, os, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CFG, HOME, secret  # noqa: E402

checks = []


def add(name, ok, fix="", required=True):
    checks.append({"check": name, "ok": bool(ok), "required": required, "fix": "" if ok else fix})


def ver(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.strip().splitlines()[0]
    except Exception:
        return ""


MAC, WIN = sys.platform == "darwin", os.name == "nt"
PY = "python" if WIN else "python3"
HERE = os.path.dirname(os.path.abspath(__file__))
inst = (lambda mac, win: win if WIN else mac)
add(f"operating system ({'macOS' if MAC else 'Windows' if WIN else sys.platform})", MAC or WIN,
    "macOS and Windows 10/11 are supported; Linux mostly works but is untested (cut-outs via rembg, schedule autopilot with cron)", required=False)
node = ver(["node", "--version"])
add(f"Node.js >= 18 ({node or 'missing'})", node and int(node.lstrip("v").split(".")[0]) >= 18, inst("brew install node", "winget install OpenJS.NodeJS.LTS"))
for tool, mac, win in (("ffmpeg", "brew install ffmpeg", "winget install Gyan.FFmpeg"), ("yt-dlp", "brew install yt-dlp", "winget install yt-dlp.yt-dlp"),
                       ("claude", "npm install -g @anthropic-ai/claude-code", "npm install -g @anthropic-ai/claude-code")):
    add(tool, shutil.which(tool), inst(mac, win))
mods = [("PIL", "pillow"), ("requests", "requests"), ("numpy", "numpy"), ("googleapiclient", "google-api-python-client"), ("google_auth_oauthlib", "google-auth-oauthlib")]
if WIN:
    mods.append(("tzdata", "tzdata"))  # Windows has no system time-zone database for zoneinfo
for mod, pkg in mods:
    try:
        importlib.import_module(mod); ok = True
    except Exception:
        ok = False
    add(f"python: {pkg}", ok, f"{PY} -m pip install --user {pkg}")
vision = MAC and os.path.exists(os.path.join(CFG, "bin", "cutout"))
try:
    importlib.import_module("rembg"); rembg = True
except Exception:
    rembg = False
add(f"photo cut-out tool ({'Apple Vision' if vision else 'rembg' if rembg else 'missing'})", vision or rembg,
    f"zsh {HERE}/build_cutout.sh   (Apple Vision, best on macOS 14+)" if MAC else f'{PY} -m pip install --user "rembg[cpu]"   (downloads a ~170 MB model on first use)')
add("Remotion installed", os.path.isdir(os.path.join(HOME, ".deps", "node_modules", "remotion")), "created automatically by the first new_channel.py (needs ~300 MB)", required=False)
for k, req, why in (("elevenlabs_api_key", True, "voice-over"), ("gemini_api_key", True, "watching reference videos + image generation"),
                    ("openai_api_key", False, "optional image provider"), ("socialbunny_api_key", False, "optional Facebook/Instagram")):
    add(f"key: {k} ({why})", secret(k, required=False), f"run in your own terminal: {PY} \"{HERE}/keys.py\" set {k}", required=req)
add("YouTube OAuth client", os.path.exists(os.path.join(CFG, "client_secret.json")), f"create a Desktop OAuth client in Google Cloud and save it as {CFG}/client_secret.json (README step 3)")
free = shutil.disk_usage(os.path.expanduser("~")).free / 1e9
add(f"disk free {free:.1f} GB (need 8+)", free >= 8, "free disk space: a long render needs ~3 GB of temp space, each finished episode ~0.5-1 GB")

if "--json" in sys.argv:
    print(json.dumps(checks, indent=1))
else:
    for c in checks:
        mark = "OK  " if c["ok"] else ("MISS" if c["required"] else "opt ")
        print(f"[{mark}] {c['check']}" + (f"\n        fix: {c['fix']}" if c["fix"] else ""))
    bad = [c for c in checks if c["required"] and not c["ok"]]
    print(f"\n{'ready' if not bad else f'{len(bad)} required item(s) missing'}")
    sys.exit(1 if bad else 0)
