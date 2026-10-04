#!/usr/bin/env python3
"""Generate one image (logo, banner, avatar, scene background) with Gemini (Nano Banana Pro) or OpenAI.

  imagegen.py "<prompt>" <out.png> [--aspect 16:9] [--size 2K] [--ref a.png --ref b.jpg] [--provider gemini|openai]

Rules this channel kit follows: never generate realistic likenesses of real people unless the channel owner explicitly
asked for it; use real licensed photos for people (commons.py + cutout). Keys: gemini_api_key / openai_api_key.
"""
import argparse, base64, mimetypes, os, sys, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from forge import secret


def gemini(prompt, out, aspect, size, refs, model):
    parts = [{"text": prompt}]
    for p in refs:
        parts.append({"inlineData": {"mimeType": mimetypes.guess_type(p)[0] or "image/png", "data": base64.b64encode(open(p, "rb").read()).decode()}})
    body = {"contents": [{"parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"imageSize": size, "aspectRatio": aspect}}}
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", params={"key": secret("gemini_api_key")}, json=body, timeout=600)
    r.raise_for_status()
    j = r.json()
    for c in j.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            if "inlineData" in p:
                open(out, "wb").write(base64.b64decode(p["inlineData"]["data"])); return
        sys.exit(f"no image returned (finishReason={c.get('finishReason')}); the prompt may have been blocked")
    sys.exit(f"no candidates: {str(j)[:300]}")


def openai(prompt, out, aspect, refs, model):
    size = {"16:9": "1536x1024", "9:16": "1024x1536", "1:1": "1024x1024"}.get(aspect, "1536x1024")
    h = {"Authorization": f"Bearer {secret('openai_api_key')}"}
    if refs:
        files = [("image[]", (os.path.basename(p), open(p, "rb"))) for p in refs]
        r = requests.post("https://api.openai.com/v1/images/edits", headers=h, data={"model": model, "prompt": prompt, "size": size}, files=files, timeout=600)
    else:
        r = requests.post("https://api.openai.com/v1/images/generations", headers=h, json={"model": model, "prompt": prompt, "size": size}, timeout=600)
    r.raise_for_status()
    open(out, "wb").write(base64.b64decode(r.json()["data"][0]["b64_json"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt"); ap.add_argument("out"); ap.add_argument("--aspect", default="16:9"); ap.add_argument("--size", default="2K")
    ap.add_argument("--ref", action="append", default=[]); ap.add_argument("--provider", default=os.environ.get("FORGE_IMAGE_PROVIDER", "gemini"))
    ap.add_argument("--model")
    a = ap.parse_args()
    if a.provider == "openai":
        openai(a.prompt, a.out, a.aspect, a.ref, a.model or "gpt-image-1")
    else:
        gemini(a.prompt, a.out, a.aspect, a.size, a.ref, a.model or "gemini-3-pro-image")
    print("saved", a.out)


if __name__ == "__main__":
    main()
