#!/usr/bin/env python3
"""Have Gemini watch a public YouTube video (by URL) and describe its format: the deepest style signal we can get
when downloads and captions are blocked. Writes markdown to stdout or --out.

  gemini_watch.py <youtube url> [--out file.md] [--model gemini-pro-latest]
Key: gemini_api_key (see common.py).
"""
import argparse, json, sys, os, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import secret

PROMPT = """You are a YouTube format analyst. Watch this video and describe its FORMAT so another creator can make
original videos in the same style (never copy its content, script, name or branding). Be concrete and measurable:
1. Structure: hook (first 30 s, word for word), segment pattern, chapter/countdown logic, outro and CTA.
2. Narration: voice type, gender, energy, words per minute (estimate), sentence length, humour, how claims are sourced.
3. Visual grammar: average shot length, what is on screen while the narrator talks (photos, cut-outs, footage, text cards,
   charts, maps, stamps), on-screen text style (font feel, colours, case), transitions, overlays, recurring graphic devices.
4. Sound: music bed, SFX usage.
5. Thumbnail and title pattern (for this video).
6. A full summary of the narration, beat by beat, with timestamps.
Return markdown with these numbered sections."""


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("url"); ap.add_argument("--out"); ap.add_argument("--model", default="gemini-pro-latest")
    a = ap.parse_args()
    key = secret("gemini_api_key")
    body = {"contents": [{"parts": [{"fileData": {"fileUri": a.url, "mimeType": "video/*"}}, {"text": PROMPT}]}]}
    for model in (a.model, "gemini-flash-latest"):
        r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", params={"key": key}, json=body, timeout=900)
        if r.ok:
            j = r.json()
            text = "".join(p.get("text", "") for c in j.get("candidates", []) for p in c.get("content", {}).get("parts", []))
            if text:
                (open(a.out, "w").write(text) if a.out else print(text))
                print(f"[gemini_watch] {model}: {len(text)} chars", file=sys.stderr)
                return
        print(f"[gemini_watch] {model} failed {r.status_code}: {r.text[:300]}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
