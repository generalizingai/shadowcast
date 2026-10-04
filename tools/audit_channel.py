#!/usr/bin/env python3
"""Audit a YouTube channel for cloning its FORMAT (never its content or branding).

  audit_channel.py <channel url or @handle> <out dir> [--top 3] [--no-video]

Writes to <out dir>:
  audit.json            channel stats, cadence, length distribution, title patterns, top videos (long + shorts)
  thumbs.jpg            contact sheet of the 12 most-viewed long-video thumbnails
  transcript_<id>.txt   auto-captions of the top long videos (+ words-per-minute in audit.json)
  frames_<id>.jpg       a frame every ~15 s from the top videos (visual grammar: cut rate, graphics, b-roll)
Needs yt-dlp and ffmpeg. Video frames are best-effort: YouTube sometimes blocks low-res downloads.
"""
import argparse, glob, json, os, re, statistics, subprocess, sys, urllib.request
from collections import Counter

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/128 Safari/537.36"}


def ytjson(args, timeout=300):
    r = subprocess.run(["yt-dlp", "-J", "--no-warnings", *args], capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[-400:])
    return json.loads(r.stdout)


def base_url(u):
    u = u.strip()
    if u.startswith("@"):
        u = "https://www.youtube.com/" + u
    return re.sub(r"/(videos|shorts|streams|featured|about)/?$", "", u.rstrip("/"))


def sheet(paths, out, cols, w=480):
    from PIL import Image
    ims = []
    for p in paths:
        try:
            im = Image.open(p).convert("RGB"); im.thumbnail((w, w)); ims.append(im)
        except Exception:
            pass
    if not ims:
        return False
    h = max(i.height for i in ims); rows = (len(ims) + cols - 1) // cols
    c = Image.new("RGB", (cols * w, rows * h), (12, 12, 16))
    for k, im in enumerate(ims):
        c.paste(im, ((k % cols) * w, (k // cols) * h))
    c.save(out, quality=85)
    return True


def storyboard(url, out_dir, vid):
    """Fallback when the video itself won't download: YouTube's own storyboard tiles (320x180 frame grids)."""
    import email
    tmp = os.path.join(out_dir, f"sb_{vid}")
    r = subprocess.run(["yt-dlp", "--no-warnings", "-f", "sb0", "-o", tmp + ".%(ext)s", url], capture_output=True, timeout=300)
    path = tmp + ".mhtml"
    if r.returncode != 0 or not os.path.exists(path):
        return []
    msg = email.message_from_bytes(open(path, "rb").read())
    imgs = []
    for k, part in enumerate(p for p in msg.walk() if p.get_content_type().startswith("image/")):
        ip = os.path.join(out_dir, f"sb_{vid}_{k:03d}.jpg"); open(ip, "wb").write(part.get_payload(decode=True)); imgs.append(ip)
    os.remove(path)
    return imgs


def subtitles(url, out_dir, vid):
    """Captions with backoff (YouTube rate-limits caption downloads with HTTP 429)."""
    import time
    for attempt in range(4):
        subprocess.run(["yt-dlp", "--no-warnings", "--skip-download", "--write-auto-subs", "--write-subs", "--sub-langs", "en,en-orig,en-US",
                        "--sub-format", "vtt", "--sleep-subtitles", "3", "-o", os.path.join(out_dir, f"sub_{vid}"), url], capture_output=True, timeout=300)
        found = glob.glob(os.path.join(out_dir, f"sub_{vid}*.vtt"))
        if found:
            return found
        time.sleep(20 * (attempt + 1))
    return []


def vtt_text(path):
    lines, last = [], ""
    for ln in open(path, encoding="utf-8", errors="ignore"):
        ln = re.sub(r"<[^>]+>", "", ln).strip()
        if not ln or "-->" in ln or ln.startswith(("WEBVTT", "Kind:", "Language:")) or ln == last:
            continue
        lines.append(ln); last = ln
    return " ".join(lines)


def title_stats(titles):
    words = [len(t.split()) for t in titles]
    caps = sum(1 for t in titles if re.search(r"\b[A-Z]{4,}\b", t))
    nums = sum(1 for t in titles if re.search(r"\d", t))
    emoji = sum(1 for t in titles if re.search(r"[\U0001F300-\U0001FAFF☀-➿]", t))
    q = sum(1 for t in titles if "?" in t)
    first = Counter(t.split()[0].lower() for t in titles if t.split())
    return {"median_words": statistics.median(words) if words else 0, "share_all_caps_word": round(caps / max(1, len(titles)), 2),
            "share_numbers": round(nums / max(1, len(titles)), 2), "share_emoji": round(emoji / max(1, len(titles)), 2),
            "share_question": round(q / max(1, len(titles)), 2), "common_first_words": first.most_common(8)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url"); ap.add_argument("out"); ap.add_argument("--top", type=int, default=3); ap.add_argument("--no-video", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    root = base_url(a.url)
    longs = ytjson(["--flat-playlist", "--playlist-end", "200", "--extractor-args", "youtubetab:approximate_date", root + "/videos"])
    try:
        shorts = ytjson(["--flat-playlist", "--playlist-end", "100", root + "/shorts"])["entries"]
    except Exception:
        shorts = []
    ents = [e for e in longs.get("entries", []) if e.get("id")]
    ts = sorted(e["timestamp"] for e in ents if e.get("timestamp"))
    per_week = round(len(ts) / max(1, (ts[-1] - ts[0]) / 604800), 2) if len(ts) > 1 else None
    recent = sorted(ts)[-20:]
    per_week_recent = round(len(recent) / max(1, (recent[-1] - recent[0]) / 604800), 2) if len(recent) > 1 else None
    durs = [e["duration"] for e in ents if e.get("duration")]
    top = sorted(ents, key=lambda e: e.get("view_count") or 0, reverse=True)
    audit = {
        "channel": longs.get("channel"), "handle": longs.get("uploader_id"), "channel_id": longs.get("channel_id"),
        "subscribers": longs.get("channel_follower_count"), "long_videos_listed": len(ents), "shorts_listed": len(shorts),
        "uploads_per_week_overall": per_week, "uploads_per_week_last20": per_week_recent,
        "duration_minutes": {"median": round(statistics.median(durs) / 60, 1) if durs else None, "p25": round(sorted(durs)[len(durs) // 4] / 60, 1) if durs else None,
                             "p75": round(sorted(durs)[3 * len(durs) // 4] / 60, 1) if durs else None},
        "titles": title_stats([e.get("title", "") for e in ents]),
        "top_long": [{"id": e["id"], "title": e.get("title"), "views": e.get("view_count"), "minutes": round((e.get("duration") or 0) / 60, 1)} for e in top[:15]],
        "top_shorts": [{"id": e["id"], "title": e.get("title"), "views": e.get("view_count")} for e in sorted(shorts, key=lambda e: e.get("view_count") or 0, reverse=True)[:10]],
        "views_median_long": statistics.median([e.get("view_count") or 0 for e in ents]) if ents else None,
        "deep_dives": [],
    }
    # thumbnails of the most-viewed long videos
    tp = []
    for e in top[:12]:
        p = os.path.join(a.out, f"thumb_{e['id']}.jpg")
        for q in ("maxresdefault", "hqdefault"):
            try:
                data = urllib.request.urlopen(urllib.request.Request(f"https://i.ytimg.com/vi/{e['id']}/{q}.jpg", headers=UA), timeout=30).read()
                if len(data) > 2000:
                    open(p, "wb").write(data); tp.append(p); break
            except Exception:
                continue
    sheet(tp, os.path.join(a.out, "thumbs.jpg"), 4)
    for p in tp:
        os.remove(p)
    # deep dives: full metadata, captions, frames
    for e in top[: a.top]:
        vid, url = e["id"], f"https://www.youtube.com/watch?v={e['id']}"
        dd = {"id": vid, "title": e.get("title"), "views": e.get("view_count")}
        try:
            full = ytjson(["--skip-download", url])
            dd.update({"upload_date": full.get("upload_date"), "tags": (full.get("tags") or [])[:25], "description": (full.get("description") or "")[:1500],
                       "chapters": [c.get("title") for c in (full.get("chapters") or [])], "minutes": round((full.get("duration") or 0) / 60, 1)})
        except Exception as ex:
            dd["meta_error"] = str(ex)[:200]
        vtts = subtitles(url, a.out, vid)
        if not vtts:
            dd["transcript_error"] = "captions unavailable or rate-limited (HTTP 429); retry later or ask the user for 1-2 transcripts"
        if vtts:
            text = vtt_text(vtts[0])
            open(os.path.join(a.out, f"transcript_{vid}.txt"), "w").write(text)
            dd["words"] = len(text.split())
            if dd.get("minutes"):
                dd["wpm"] = round(len(text.split()) / dd["minutes"])
            for v in vtts:
                os.remove(v)
        if not a.no_video:
            tmp = os.path.join(a.out, f"v_{vid}.mp4")
            r = subprocess.run(["yt-dlp", "--no-warnings", "-f", "worst[height>=240][ext=mp4]/worst[height>=240]/worst", "-o", tmp, url], capture_output=True, timeout=900)
            if r.returncode == 0 and os.path.exists(tmp):
                fdir = os.path.join(a.out, f"fr_{vid}"); os.makedirs(fdir, exist_ok=True)
                subprocess.run(["ffmpeg", "-v", "error", "-i", tmp, "-vf", "fps=1/15,scale=480:-1", os.path.join(fdir, "%03d.jpg")], timeout=600)
                frames = sorted(glob.glob(os.path.join(fdir, "*.jpg")))
                sheet(frames[:48], os.path.join(a.out, f"frames_{vid}.jpg"), 6)
                dd["frames_sheet"] = f"frames_{vid}.jpg"; dd["frames"] = len(frames)
                for p in frames:
                    os.remove(p)
                os.rmdir(fdir); os.remove(tmp)
            else:
                tiles = storyboard(url, a.out, vid)
                if tiles and sheet(tiles[:12], os.path.join(a.out, f"frames_{vid}.jpg"), 3, w=960):
                    dd["frames_sheet"] = f"frames_{vid}.jpg"; dd["frames_note"] = "storyboard tiles (low-res grids, ~1 frame per few seconds)"
                else:
                    dd["frames_error"] = "video and storyboard blocked; rely on thumbnails + transcript"
                for t in tiles:
                    os.remove(t)
        audit["deep_dives"].append(dd)
    json.dump(audit, open(os.path.join(a.out, "audit.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: audit[k] for k in ("channel", "subscribers", "long_videos_listed", "shorts_listed", "uploads_per_week_last20", "duration_minutes")}, ensure_ascii=False))
    print("deep dives:", [(d["id"], d.get("wpm"), d.get("frames_sheet") or d.get("frames_error")) for d in audit["deep_dives"]])


if __name__ == "__main__":
    main()
