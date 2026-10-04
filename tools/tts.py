"""Episode voiceover with ElevenLabs, one request per script section ("## " headings in SCRIPT.md, "**VO:**" lines).
Writes audio/vo.mp3, audio/VO.txt, audio/words.json [{w,s,e}], audio/sections.json [{name,s,e}].

  tts.py <episode dir> [--voice ID] [--model eleven_v4] [--only N]
Voice/model default to channel.json ("voice": {"id", "model", "respell": [["7-Eleven","Seven-Eleven"]]}) two levels up.
Key: elevenlabs_api_key (see forge.py)."""
import argparse, base64, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from forge import secret

ap = argparse.ArgumentParser(); ap.add_argument("episode"); ap.add_argument("--voice"); ap.add_argument("--model"); ap.add_argument("--only", type=int)
ARGS = ap.parse_args()
ROOT = os.path.abspath(ARGS.episode)
CH = os.path.join(os.path.dirname(os.path.dirname(ROOT)), "channel.json")
VCFG = json.load(open(CH)).get("voice", {}) if os.path.exists(CH) else {}
AUD = os.path.join(ROOT, "audio")
PARTS = os.path.join(AUD, "parts")
VOICE = ARGS.voice or VCFG.get("id") or sys.exit("no voice id: set channel.json voice.id or pass --voice")
MODEL = ARGS.model or VCFG.get("model", "eleven_v4")
GAP = 0.45  # seconds of silence between sections
FIXES = [tuple(x) for x in VCFG.get("respell", [])]  # TTS-only respellings; captions keep the original words


def sections():
    out, cur = [], None
    for line in open(os.path.join(ROOT, "SCRIPT.md")):
        if line.startswith("## "):
            cur = {"name": re.sub(r"\s*\(.*\)", "", line[3:]).strip(), "lines": []}
            out.append(cur)
        elif line.startswith("**VO:**") and cur:
            t = line.replace("**VO:**", "").strip()
            for a, b in FIXES:
                t = t.replace(a, b)
            cur["lines"].append(t)
    return [s for s in out if s["lines"]]


def words_from(al, off):
    ch, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    out, cur, s, pe = [], "", None, None
    for c, b, e in zip(ch, st, en):
        if c.isspace():
            if cur:
                out.append({"w": cur, "s": round(s + off, 3), "e": round(pe + off, 3)})
                cur = ""
        else:
            if not cur:
                s = b
            cur += c
            pe = e
    if cur:
        out.append({"w": cur, "s": round(s + off, 3), "e": round(pe + off, 3)})
    return out


def tts(i, text):
    key = secret("elevenlabs_api_key")
    body = {"text": text, "model_id": MODEL,
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True}}
    r = subprocess.run(["curl", "-s", f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128",
                        "-H", f"xi-api-key: {key}", "-H", "Content-Type: application/json", "-d", json.dumps(body)],
                       capture_output=True, text=True)
    data = json.loads(r.stdout)
    if "audio_base64" not in data:
        sys.exit(f"section {i} FAILED: {str(data)[:400]}")
    open(os.path.join(PARTS, f"{i:02d}.mp3"), "wb").write(base64.b64decode(data["audio_base64"]))
    json.dump(data["alignment"], open(os.path.join(PARTS, f"{i:02d}.json"), "w"))


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode())


def main():
    os.makedirs(PARTS, exist_ok=True)
    secs = sections()
    only = ARGS.only
    open(os.path.join(AUD, "VO.txt"), "w").write("\n\n".join("\n".join(s["lines"]) for s in secs) + "\n")
    for i, s in enumerate(secs):
        if only is None and os.path.exists(os.path.join(PARTS, f"{i:02d}.mp3")):
            continue
        if only is not None and i != only:
            continue
        txt = " ".join(s["lines"])
        print(f"[{i}] {s['name']}: {len(txt)} chars", flush=True)
        tts(i, txt)
    # stitch: each part re-encoded to wav, then concatenated with fixed gaps
    words, smap, off, lst = [], [], 0.0, []
    sil = os.path.join(PARTS, "gap.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono", "-t", str(GAP), sil], check=True)
    for i, s in enumerate(secs):
        mp = os.path.join(PARTS, f"{i:02d}.mp3")
        wv = os.path.join(PARTS, f"{i:02d}.wav")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp, "-ar", "44100", "-ac", "1", wv], check=True)
        d = dur(wv)
        words += words_from(json.load(open(os.path.join(PARTS, f"{i:02d}.json"))), off)
        smap.append({"name": s["name"], "s": round(off, 3), "e": round(off + d, 3)})
        lst += [wv, sil]
        off += d + GAP
    open(os.path.join(PARTS, "list.txt"), "w").write("".join(f"file '{p}'\n" for p in lst[:-1]))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(PARTS, "list.txt"),
                    "-c:a", "libmp3lame", "-b:a", "192k", os.path.join(AUD, "vo.mp3")], check=True)
    json.dump(words, open(os.path.join(AUD, "words.json"), "w"))
    json.dump(smap, open(os.path.join(AUD, "sections.json"), "w"), indent=1)
    print(f"done: {off - GAP:.1f}s, {len(words)} words, {len(secs)} sections")


if __name__ == "__main__":
    main()
