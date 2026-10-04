---
name: episode
description: Produce one complete episode for a channel-forge channel. Covers research, fact sheet, script, approval gate, voice-over, photos, word-synced motion graphics, layout audit, render, two native Shorts, thumbnails and the upload package. It resumes from the episode's saved status. Use for "make the next video", "new episode about X", or to continue an unfinished one.
argument-hint: <channel slug> [topic or episode ID]
---

# Episode pipeline

```
T="${CLAUDE_PLUGIN_ROOT}/tools"
W="${FORGE_HOME:-$HOME/ChannelForge}/<slug>"
```

Read these before starting:
- `W/channel.json`
- `W/STYLE.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/episode/references/RULES.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/episode/references/KIT.md`

Then run `python3 "$T/ep.py" list <slug>`.
- If an episode ID is given, or one is unfinished, **resume it at its status**.
- Otherwise start a new one.

After each stage, record it with `python3 "$T/ep.py" set <slug> <ID> <status>` so a crash or a new session continues where it stopped.

## 1. planned → researched
1. **Pick the topic.**
   - If none was given, take the best unused idea from STYLE.md "Topics".
   - Check it isn't a repeat: compare against the existing episode titles.
   - Use WebSearch to check it's timely or evergreen.
2. **Create the episode.** Run `python3 "$T/ep.py" new <slug> "<working title>"`. It prints `{id, dir, src}`.
3. **Research.**
   - Use WebSearch/WebFetch on primary and reputable sources: court records, major outlets, official stats, the person's own statements.
   - Record 2+ sources for any serious claim.
4. **Fill `dir/FACTSHEET.md`.** Every claim, its exact status, and its source; a "Never say" list; numbers with units; the Sources list (outlet, "headline", date, URL).
5. Set status `researched`.

## 2. researched → scripted → awaiting_approval
1. **Write `dir/SCRIPT.md`** from the template.
   - Sections are `## ` headings, and every voiced line starts with `**VO:**`.
   - Section names drive the rail:
     - countdown: `COLD OPEN`, `#10 NAME` … `#1 NAME`, `OUTRO`
     - chapters: `COLD OPEN`, `CHAPTER 1: TITLE` …, `OUTRO`
   - Length = minutes × wpm words.
2. **Self-check against FACTSHEET line by line.** Every sentence must be supported; fix or cut anything that isn't.
3. If `meta.feedback` exists, this is a rewrite: address every point, then clear it with `python3 "$T/ep.py" set <slug> <ID> scripted feedback=`.
4. **Approval gate.** Set `awaiting_approval`, then run `python3 "$T/notify.py" <slug> "Script ready: <ID>" "<title>. Approve with /channel-forge:approve <slug> <ID>"`. What happens next depends on the session:
   - **Interactive session:** show the user the title, a 5-line summary, the claim count and the path. Ask whether to approve now.
   - **Autopilot:** stop work on this episode. `ep.py next` decides when it may continue: after the approval window in `optional` mode; never automatically when `real_people` is true or mode is `required`.
5. When approved: set `approved`.

## 3. approved → voiced
1. `python3 "$T/tts.py" "<dir>"`: one ElevenLabs request per section, with timestamps.
   - Add pronunciation fixes to `channel.json voice.respell` (e.g. `[["Nguyen","Win"]]`).
2. `python3 "$T/tighten.py" "<dir>" <tempo>`: caps pauses at 0.32 s, tempo from `voice.tempo` (default 1.1).
   - It writes `audio/vo_tight.wav`, `words_tight.json` and `sections_tight.json`.
3. Listen-check by reading `words_tight.json` around tricky names. Check the total duration is within ±15% of the target.
4. Set `voiced`.

## 4. voiced → built
1. **Photos.** Start fetching people and backgrounds early. For each item, follow the RULES "Assets" section:
   - Search: `python3 "$T/commons.py" search "<query>"`.
   - Fetch: `python3 "$T/commons.py" fetch "<dir>/assets/web" p_<name> "File:<title>"`.
   - Cut out: `~/.config/channel-forge/bin/cutout "<dir>/assets/web/p_<name>.jpg" "<dir>/assets/cut/<name>.png"`.
   - **Look at every cut-out.**
   - Run several fetches in a background agent if it's slow. Build with stand-ins meanwhile.
2. **Long video shots.** Write `src/shots.tsx`, splitting into `shots1.tsx`/`shots2.tsx` past ~40 shots.
   - One shot per beat, every 4-8 s, word-anchored with marks for each reveal.
   - Vary the components and follow the STYLE visual grammar.
   - Cold open: `TitleCard`, or a `Lineup`/`Teasers` hook. Each countdown item opens with `Countdown`. Outro ends with `Choices` then `EndCard`.
3. **Shorts.** Pick 2 sections (strongest hook; #1 or payoff) and write `short1.tsx` / `short2.tsx` with fresh 9:16 shots for that section.
4. **Thumbnails.** Write `thumbs.tsx` with ThumbA/B/C (see RULES).
5. **`index.tsx`.** Use `makeEpisode({ words: W_, sections: S_, shots: SHOTS, rail, total })` and the EpisodeEntry ids `<ID>`, `<ID>Short1`, `<ID>Short2`, `<ID>ThumbA/B/C`.
   - `rail` is `"countdown"` with `total` = item count, or `"chapters"`.
6. **Register and typecheck.** Run `python3 "$T/ep.py" register <slug> <ID>`, then `cd "$W/studio" && npx tsc --noEmit -p .`, and fix every error.
7. Set `built`.

## 5. built → audited (do not skip)
1. Run `python3 "$T/audit_layout.py" "$W/studio" "<dir>" <ID>`.
2. Open **every** sheet it prints with Read. Check each frame against the RULES "Layout" list.
3. Fix, re-run, and look again until a full pass is clean.
4. Also view the thumbnails: `npx remotion still` each one into the scratchpad.
5. Set `audited`.

## 6. audited → rendered
1. Check the disk with `df -h ~`. You need about 3 GB free.
2. Run `zsh "$T/render_episode.sh" <slug> <ID>`. It writes `out/long.mp4`, `short1.mp4`, `short2.mp4` and `thumb_A/B/C.jpg`. A 10-minute video takes about 10-25 minutes.
3. Verify: `ffprobe` the durations, extract and view about 6 frames from the long video and 3 per Short (`ffmpeg -ss <t> -i <f> -frames:v 1 <scratch>.jpg`), and view the thumbnails.
4. Set `rendered`.

## 7. rendered → packaged
1. Add a `"package"` section to `dir/meta.json`. The format is in `tools/package.py`'s docstring:
   - 3-4 title options (main first, under 70 characters, following the STYLE title formula)
   - summary (2-3 sentences, keyword-rich, accurate), cta, 12-18 tags
   - chapter_names if the section names need prettifying
   - accuracy notes, the thumbnail letter
   - the two shorts: role, title with `#shorts`, hook, social caption, sources
2. Run `python3 "$T/package.py" <slug> <ID>`.
3. Set `packaged`.

## 8. packaged → scheduled
Hand off to the publish skill (`/channel-forge:publish <slug> <ID>`), or follow its steps directly.
