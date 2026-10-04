---
name: brand-kit
description: Create an original identity for a new channel. Covers the name, handle, colours, fonts, wordmark, monogram, avatar, banner and voice, and writes them into the channel workspace. Use after a channel audit, or when a channel needs a rebrand.
argument-hint: <channel slug>
---

# Brand kit

`T="${CLAUDE_PLUGIN_ROOT}/tools"`. Workspace `W=${FORGE_HOME:-~/ChannelForge}/<slug>`. Read `W/STYLE.md` and `W/channel.json` first.

The identity must be **ours**. It must not be confusable with the reference channel or any brand: no similar name, logo shape or signature colour combination. It should still fit the niche's mood, as the audit describes it.

## 1. Name + handle
- Brainstorm 12 names: short (1-2 words), easy to say, ownable, fitting the niche.
- Shortlist 4. For each, check:
  - the handle: `curl -s -o /dev/null -w "%{http_code}" https://www.youtube.com/@<handle>` (404 means likely free);
  - a WebSearch for "<name>" YouTube, plus trademark conflicts.
  Drop any name that collides.
- If the user is present, offer the 4 with one line each and let them pick. In autopilot, take the best one.
- Write `name`, `handle`, `tagline` (under 8 words), `youtube.channel_title` and `code` (2-4 capitals) into channel.json.
  - `new_channel.py` sets `code` at creation; keep it unless it's empty.

## 2. Look
- Choose `brand.colors` (all 11 roles, `#RRGGBB`):
  - background ramp: deep, navy, navy2 (any dark hue);
  - accent ramp: gold, gold2, goldDeep (the accent can be any hue: teal, crimson, lime...);
  - text: ivory, dim; plus paper, red, green.
- Choose `brand.fonts` by Google Fonts family name:
  - `serif` (display and headlines), `sans` (UI and labels), `cond` (condensed impact text), `type` (typewriter or mono for documents).
  - They must exist in @remotion/google-fonts. Common safe picks: Playfair Display, DM Serif Display, Fraunces, Bodoni Moda, Inter, Manrope, Montserrat, Anton, Bebas Neue, Oswald, Courier Prime, IBM Plex Mono.
- Run `python3 "$T/new_channel.py" brand <slug>`. It validates the fonts and colours, and writes the studio's brand.ts.

## 3. Images (`W/brand/`)
Use `python3 "$T/imagegen.py" "<prompt>" <out> --aspect <a>`. Generate, then **look at every result** with Read and regenerate until it is clean.
- `wordmark.png`: the channel name in light lettering on a transparent or very dark background, wide (about 8:1).
  - Image models are unreliable at text. If the lettering isn't letter-perfect, build the wordmark from the brand font in Remotion or with PIL instead.
  - Never ship a misspelt wordmark.
- `mono.png`: square monogram (1:1, 512 px), readable at 54 px.
- `avatar.png`: 800x800 profile picture, a bold mark that survives a circle crop.
- `banner.png` / `banner.jpg`: 2560x1440, under 6 MB.
  - ALL text and logo must sit inside the centred **1546x423 safe area** (what phones show). Edges are decoration only.
  - Prompt the safe-area constraint explicitly. Then crop the centre 1546x423 and check that nothing important is cut.
- Copy wordmark/mono into existing episodes: `python3 "$T/new_channel.py" brand <slug>` again.

## 4. Voice
- Choose an ElevenLabs voice that matches STYLE.md (gender, age, energy, accent).
  - List voices: `curl -s https://api.elevenlabs.io/v1/voices -H "xi-api-key: $KEY"`. Get KEY from `python3 -c "import sys;sys.path.insert(0,'$T');from forge import secret;print(secret('elevenlabs_api_key'))"`, and never print it.
  - Prefer the user's own cloned voice if they have one.
- Write `voice.id`, `voice.name` and `voice.model` ("eleven_v4", or "eleven_multilingual_v2" if the account lacks v4).

## 5. Channel description
Write `W/brand/description.txt`: up to 1000 characters, saying what the channel is and its upload days. Add 10-15 `youtube.keywords`.

Finish with a short summary and the paths of the avatar and banner.
