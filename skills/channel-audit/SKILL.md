---
name: channel-audit
description: Audit a reference YouTube channel and write the style bible (STYLE.md) for our own original channel in the same format. Use when given a channel link to learn from, or to refresh what a channel's style is based on.
argument-hint: <youtube channel url or @handle> <our channel slug>
---

# Channel audit → STYLE.md

`T="${CLAUDE_PLUGIN_ROOT}/tools"`. Audit folder `A`: `${SHADOWCAST_HOME:-~/Shadowcast}/<slug>/audit` if the channel workspace exists; otherwise `${SHADOWCAST_HOME:-~/Shadowcast}/_audits/<reference handle>`. The clone-channel flow moves it into the workspace once the channel exists. Steps 5-6 need the workspace.

We learn a channel's **format** (structure, pacing, visual grammar, packaging) so we can make **original** videos in that format. We never copy its name, logo, colours-as-identity, scripts, thumbnails, footage or exact titles.

## Steps
1. **Numbers.** Run `python3 "$T/audit_channel.py" "<url>" "$A" --top 3`. This writes `audit.json`, `thumbs.jpg` and `frames_<id>.jpg`, and also `transcript_<id>.txt` when captions are reachable. It takes 2-6 minutes.
   - Captions often fail with HTTP 429. That is expected; carry on.
2. **Watch.** For each of the top 2 long videos, run `python3 "$T/gemini_watch.py" "https://www.youtube.com/watch?v=<id>" --out "$A/watch_<id>.md"`.
   - Also watch 1 top Short if the channel makes Shorts.
   - If Gemini fails, continue with the frames, thumbnails and transcripts you have.
3. **Look.** Open `thumbs.jpg` and every `frames_*.jpg` with Read, and actually study them.
   - Count the distinct graphic devices: photo backgrounds, cut-outs, text cards, charts, stamps, maps, rails.
   - Note the colour mood and type feel.
   - Estimate the shot length.
4. **Map to our kit.** Read `${CLAUDE_PLUGIN_ROOT}/skills/episode/references/KIT.md`. For each device they use, name the kit component that delivers it, or the closest one.
   - If a device is essential and the kit lacks it, note "NEW COMPONENT: <what>". The episode skill builds it in the channel's studio.
5. **Write `<workspace>/STYLE.md`** from `${CLAUDE_PLUGIN_ROOT}/templates/STYLE.md`. Fill every section with concrete numbers and with examples that are our own.
   - Include 20 ranked topic ideas, each fitting our channel. Never re-do their exact videos.
   - Pick the closest format type (`countdown` or `chapters`) and target minutes.
   - Set wpm = transcript words / minutes, or Gemini's estimate, or 165.
6. **Update `channel.json`** with these fields:
   - `source.audited` (today), `niche`
   - `real_people`: true if videos are about real, identifiable people
   - `format`: type, rail, minutes, items, wpm
   - `hashtags`
   - `schedule.days`: keep the user's choice. If they have none, use the reference cadence capped at 3 per week.
7. Report the result in 5 lines: what makes the channel work, the format we'll use, cadence, and 3 example titles.
