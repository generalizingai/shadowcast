"""Shared helpers for shadowcast tools: paths, per-channel config, and secret lookup.

Workspace (SHADOWCAST_HOME, default ~/Shadowcast):
  <slug>/channel.json   name, handle, target channel, niche, voice, cadence, approval, platforms
  <slug>/STYLE.md       style bible written from the audit
  <slug>/brand/         logo, monogram, banner, avatar, brand.json
  <slug>/studio/        Remotion project (copied from studio-template)
  <slug>/episodes/<NN-slug>/  FACTSHEET.md SCRIPT.md audio/ assets/ out/ meta.json publish.json
  <slug>/calendar.json  booked release dates
Secrets: ~/.config/shadowcast/keys.json (written by keys.py, mode 600), or env SHADOWCAST_<NAME> / <NAME>.
"""
import json, os, sys

HOME = os.path.expanduser(os.environ.get("SHADOWCAST_HOME", "~/Shadowcast"))
CFG = os.path.expanduser("~/.config/shadowcast")
PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def secret(name, required=True):
    """name like 'elevenlabs_api_key'."""
    for k in (f"CLAUDE_PLUGIN_OPTION_{name.upper()}", f"SHADOWCAST_{name.upper()}", name.upper()):
        if os.environ.get(k):
            return os.environ[k].strip()
    p = os.path.join(CFG, "keys.json")
    if os.path.exists(p):
        v = json.load(open(p)).get(name)
        if v:
            return v.strip()
    if required:
        sys.exit(f"missing secret '{name}': run `python3 {os.path.dirname(os.path.abspath(__file__))}/keys.py set {name}` in a terminal")
    return None


def channel_dir(slug):
    d = os.path.join(HOME, slug)
    if not os.path.isdir(d):
        sys.exit(f"no channel workspace at {d}")
    return d


def channel(slug):
    return json.load(open(os.path.join(channel_dir(slug), "channel.json")))


def save_channel(slug, data):
    json.dump(data, open(os.path.join(channel_dir(slug), "channel.json"), "w"), indent=1, ensure_ascii=False)
