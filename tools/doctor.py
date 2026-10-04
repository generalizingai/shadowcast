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


add("macOS", sys.platform == "darwin", "shadowcast's cut-out tool and scheduler are macOS-only for now")
node = ver(["node", "--version"])
add(f"Node.js >= 18 ({node or 'missing'})", node and int(node.lstrip("v").split(".")[0]) >= 18, "brew install node")
for tool, fix in (("ffmpeg", "brew install ffmpeg"), ("yt-dlp", "brew install yt-dlp"), ("claude", "npm install -g @anthropic-ai/claude-code")):
    add(tool, shutil.which(tool), fix)
for mod, pkg in (("PIL", "pillow"), ("requests", "requests"), ("googleapiclient", "google-api-python-client"), ("google_auth_oauthlib", "google-auth-oauthlib")):
    try:
        importlib.import_module(mod); ok = True
    except Exception:
        ok = False
    add(f"python: {pkg}", ok, f"python3 -m pip install --user {pkg}")
add("cut-out tool (Apple Vision)", os.path.exists(os.path.join(CFG, "bin", "cutout")), f"zsh {os.path.dirname(os.path.abspath(__file__))}/build_cutout.sh")
add("Remotion installed", os.path.isdir(os.path.join(HOME, ".deps", "node_modules", "remotion")), "created automatically by the first new_channel.py (needs ~300 MB)", required=False)
for k, req, why in (("elevenlabs_api_key", True, "voice-over"), ("gemini_api_key", True, "watching reference videos + image generation"),
                    ("openai_api_key", False, "optional image provider"), ("socialbunny_api_key", False, "optional Facebook/Instagram")):
    add(f"key: {k} ({why})", secret(k, required=False), f"run in your terminal: python3 {os.path.dirname(os.path.abspath(__file__))}/keys.py set {k}", required=req)
add("YouTube OAuth client", os.path.exists(os.path.join(CFG, "client_secret.json")), f"create a Desktop OAuth client in Google Cloud and save it as {CFG}/client_secret.json (README step 3)")
st = os.statvfs(os.path.expanduser("~"))
free = st.f_bavail * st.f_frsize / 1e9
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
