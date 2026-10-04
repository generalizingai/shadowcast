---
name: demo
description: Quick Shadowcast trial. Give it a YouTube channel link and it produces ONE 1-minute demo video in that channel's format, plus 1 Short and 1 thumbnail. Nothing is published and no YouTube account is needed. Use when someone wants to try Shadowcast or see what it makes before setting up a real channel.
argument-hint: <youtube channel url or @handle> [topic]
---

# Demo: 1-minute video from a channel link (no publishing)

`T="${CLAUDE_PLUGIN_ROOT}/tools"`, `H="${SHADOWCAST_HOME:-$HOME/Shadowcast}"`. Target: 20-35 minutes end to end.

This runs the real pipeline at small scale, with the same quality rules. Nothing goes to YouTube. Post one short progress line at each step.

## 0. Ready check
Run `python3 "$T/doctor.py"`.
- Needed: node, ffmpeg, yt-dlp, the python packages, the cut-out tool, and the `elevenlabs_api_key` and `gemini_api_key` keys.
- Not needed: YouTube OAuth.
- If something required is missing, give the exact fix and stop. Keys are set by the user in their own terminal: `python3 "$T/keys.py" set <name>`.
- You need 3 GB free.

## 1. Light audit (about 5 min)
1. Run `python3 "$T/audit_channel.py" "<url>" "$H/_audits/<handle>" --top 1`.
2. Run `python3 "$T/gemini_watch.py" "https://www.youtube.com/watch?v=<top id>" --out "$H/_audits/<handle>/watch.md"`. If it fails, continue without it.
3. Look at `thumbs.jpg` and the frames sheet.
4. Write 5 lines: format, tone, visual devices, pacing, thumbnail style.

## 2. Demo channel (no questions asked)
1. Create the channel: `python3 "$T/new_channel.py" demo-<handle> --name "<an original name you invent>" --code DM --source "<url>"`.
   - The name must be original and not confusable with the reference channel.
   - Don't run handle or trademark checks; this is a demo.
2. Move the audit in: `mv "$H/_audits/<handle>" "$H/demo-<handle>/audit"`.
3. In channel.json, set:
   - `brand.source` = "match"
   - colours from `python3 "$T/brand_extract.py" palette "$H/demo-<handle>/audit/thumbs.jpg"`
   - fonts closest to the reference type feel
   - `format`: minutes 1, items 3, rail "countdown" (or "chapters" if the reference tells stories)
   - `voice`: pick an ElevenLabs voice that fits the reference tone
   - `real_people` as appropriate
4. Make logos with no image model: `python3 "$T/wordmark.py" demo-<handle>`. It renders the name in the brand font and colours, so the spelling is always exact.
5. Run `python3 "$T/new_channel.py" brand demo-<handle>`.

## 3. One 1-minute episode
Follow the episode skill (`${CLAUDE_PLUGIN_ROOT}/skills/episode/SKILL.md` plus its references) with these demo changes:
- **Topic:** the given one, or the best evergreen fit for the format. For a fast demo, prefer a topic with easy, well-documented facts.
- **Research:** 3-6 solid sources, and a short FACTSHEET.
- **Script:** **150-170 words total**. Sections are `COLD OPEN`, three items (`#3`, `#2`, `#1`, or 3 short chapters) and a one-line `OUTRO`.
- **Approval:** show the script in chat and continue straight away. Nothing is published, so there's no gate. Record `scripted` → `approved`.
- **Visuals:**
  - 8-12 shots. Use real licensed photos (commons.py + cutout) where the topic has people; otherwise use kit graphics.
  - **One Short only** (`short1.tsx`, from the strongest section) and **one thumbnail** (`ThumbA`).
- **Audit:** run the layout audit fully. Don't skip it, even in a demo.
- **Render:** `zsh "$T/render_episode.sh" demo-<handle> DM01`. It takes about 3-6 minutes.
- **Skip** packaging, scheduling and autopilot.

## 4. Show the result
- Run `open "<episode dir>/out"` and send the user `long.mp4`, `short1.mp4` and `thumb_A.jpg`.
- Show 4 frames from the long video.
- Say what to tweak: voice, colours, pacing, topic.
- Say that `/shadowcast:clone-channel <url>` sets up the real channel. The demo channel folder can be reused or deleted.
