"""Facebook + Instagram through SocialBunny's REST scheduler (optional; https://socialbunny-api.onrender.com).

channel.json "social": {"socialbunny": {"facebook": "<page handle>", "instagram": "<ig handle>", "fb_reels": true}}
API key (sbk_...): plugin setting socialbunny_api_key (or FORGE_SOCIALBUNNY_API_KEY / ~/.config/channel-forge/keys.json).
  1. POST /media/upload-url {filename, contentType} -> signed PUT url + public url
  2. POST /scheduler/posts {caption, mediaUrls, scheduledAt (UTC Z), targets:[{connectionId, format:"video", options}]}
SocialBunny publishes due posts from its own cron, so posts can land a few minutes after their slot.
"""
import json, os, sys, time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from forge import channel, secret  # noqa: E402

API = os.environ.get("SOCIALBUNNY_API", "https://socialbunny-api.onrender.com")
SLUG = None  # set by publish.py


def cfg():
    s = (channel(SLUG).get("social") or {}).get("socialbunny")
    if not s:
        sys.exit(f"SocialBunny is not configured for {SLUG} (channel.json social.socialbunny)")
    return s


def _call(method, path, **kw):
    for i in range(4):  # Render's free tier sleeps: the first request can take ~1 min
        try:
            r = requests.request(method, API + path, headers={"Authorization": f"Bearer {secret('socialbunny_api_key')}"}, timeout=120, **kw)
        except requests.RequestException as e:
            if i == 3:
                raise SystemExit(f"SocialBunny unreachable: {e}")
            time.sleep(10 * (i + 1)); continue
        if r.status_code >= 500 and i < 3:
            time.sleep(10 * (i + 1)); continue
        if r.status_code >= 400:
            raise SystemExit(f"SocialBunny {method} {path} -> {r.status_code}: {r.text[:300]}")
        return r.json()


def accounts():
    """{'facebook': connection_id, 'instagram': connection_id} for this channel's configured handles only."""
    want = {p: h for p, h in cfg().items() if p in ("facebook", "instagram") and h}
    rows = _call("GET", "/scheduler/accounts")["accounts"]
    norm = lambda s: (s or "").lower().replace(" ", "").lstrip("@")
    out = {}
    for plat, handle in want.items():
        hits = [a for a in rows if a["platform"] == plat and norm(a["handle"]) == norm(handle)]
        if len(hits) != 1:
            raise SystemExit(f"expected exactly one {plat} account '{handle}' in SocialBunny, found {[a['handle'] for a in rows if a['platform'] == plat]}")
        out[plat] = hits[0]["id"]
    return out


def upload(path):
    s = _call("POST", "/media/upload-url", json={"filename": os.path.basename(path).replace(" ", "-"), "contentType": "video/mp4"})
    with open(path, "rb") as fh:
        r = requests.put(s["uploadUrl"], data=fh, headers={"Content-Type": "video/mp4"}, timeout=1800)
    if r.status_code >= 400:
        raise SystemExit(f"video upload failed {r.status_code}: {r.text[:300]}")
    return s["publicUrl"]


def schedule(caption, media_url, publish_at, platforms, acc, reel=False):
    fb_reel = reel and cfg().get("fb_reels", False)
    tgt = lambda p: {"connectionId": acc[p], "format": "video", **({"options": {"fbReel": True}} if p == "facebook" and fb_reel else {})}
    body = {"caption": caption, "mediaUrls": [media_url], "scheduledAt": publish_at, "targets": [tgt(p) for p in platforms if p in acc]}
    r = _call("POST", "/scheduler/posts", json=body)
    if not r.get("scheduled"):
        raise SystemExit(f"SocialBunny did not schedule the post: {json.dumps(r)[:300]}")
    return r["id"]


def posts(limit=30):
    return _call("GET", f"/scheduler/posts?limit={limit}")
