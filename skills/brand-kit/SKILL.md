---
name: brand-kit
description: Set a channel's identity (name, handle, colours, fonts, wordmark, monogram, avatar, banner, voice) from the user's own brand files, their website, or (default) by matching the reference channel's look with an original name and logo. Use after a channel audit, or for a rebrand.
argument-hint: <channel slug> [brand folder | website url]
---

# Brand kit

`T="${CLAUDE_PLUGIN_ROOT}/tools"`. Workspace `W=${FORGE_HOME:-~/ChannelForge}/<slug>`. Read `W/STYLE.md` and `W/channel.json` first.

## 0. Brand source (`channel.json brand.source`)
Pick exactly one. The user's choice wins, so ask if it's unknown and they're present.

| source | when | what we take |
|---|---|---|
| `own` | the user gave a folder of brand files | their exact files and colours; fonts by name |
| `website` | the user gave their site URL | the site's name, tagline, logo, colours and fonts |
| `match` (default) | nothing given | the reference channel's **look** (palette, font feel, thumbnail and layout grammar) with an **original** name, logo, avatar and banner |

- **own:** run `python3 "$T/brand_extract.py" folder "<folder>" "$W/brand/source"`.
  - Use their logo files as-is; never redraw or "improve" them. Copy the best light-on-dark version to `brand/wordmark.png`, and a square mark to `brand/mono.png` and `brand/avatar.png`. Only fill in what's missing (e.g. generate a banner in their colours, with their logo placed in the safe area).
  - Colours come from `suggested_roles`, then adjust: keep their exact brand hex as the `gold` accent. Text files in the folder may name their fonts.
  - Name and handle come from the user. Skip step 1 unless they're missing.
- **website:** run `python3 "$T/brand_extract.py" site "<url>" "$W/brand/source"`.
  - Look at every downloaded `site_logo_*` file. Pick the real logo; og-images are often photos, so ignore those.
  - Name and tagline come from the site. Colours come from `suggested_roles`; the site's primary brand colour becomes `gold`.
  - Fonts: use the site's fonts if they're Google Fonts. Otherwise use the closest Google Font (e.g. a custom grotesk becomes Inter or Manrope).
  - Then continue as `own`, using the extracted logo.
- **match:** run `python3 "$T/brand_extract.py" palette "$W/audit/thumbs.jpg" "$W"/audit/frames_*.jpg`.
  - Copy the palette roles, and choose the Google Fonts closest to their type feel (serif vs grotesk vs condensed). The videos and thumbnails should feel like the reference channel.
  - Never reuse their name, wordmark, logo, avatar, banner art, catchphrase sign-offs or mascot. Never create a confusingly similar name or logo either: no sound-alikes, no same initials in the same badge shape.
  - Why this rule matters: YouTube terminates channels for impersonation (copied name/avatar/banner), and channel names and logos are often trademarked. The look itself (colours, fonts, layout style) is fine to match.
  - If the user insists on copying another channel's name or logo, explain the risk and decline. The exception is a channel they own or have written permission for; then treat it as `own`.

Record `brand.source` (and `brand.source_ref`: the folder, URL or reference channel) in channel.json.

## 1. Name + handle (match mode, or when own/website gave none)
- Brainstorm 12 names: short (1-2 words), easy to say, ownable, fitting the niche.
- Shortlist 4. For each, check:
  - the handle: `curl -s -o /dev/null -w "%{http_code}" https://www.youtube.com/@<handle>` (404 means likely free);
  - a WebSearch for "<name>" YouTube, plus trademark conflicts.
  Drop any name that collides.
- If the user is present, offer the 4 with one line each and let them pick. In autopilot, take the best one.
- Write `name`, `handle`, `tagline` (under 8 words), `youtube.channel_title` and `code` (2-4 capitals) into channel.json.
  - `new_channel.py` sets `code` at creation; keep it unless it's empty.

## 2. Look
- Start from step 0's `suggested_roles`. Choose `brand.colors` (all 11 roles, `#RRGGBB`):
  - background ramp: deep, navy, navy2 (any dark hue);
  - accent ramp: gold, gold2, goldDeep (the accent can be any hue: teal, crimson, lime...);
  - text: ivory, dim; plus paper, red, green.
- Choose `brand.fonts` by Google Fonts family name:
  - `serif` (display and headlines), `sans` (UI and labels), `cond` (condensed impact text), `type` (typewriter or mono for documents).
  - They must exist in @remotion/google-fonts. Common safe picks: Playfair Display, DM Serif Display, Fraunces, Bodoni Moda, Inter, Manrope, Montserrat, Anton, Bebas Neue, Oswald, Courier Prime, IBM Plex Mono.
- Run `python3 "$T/new_channel.py" brand <slug>`. It validates the fonts and colours, and writes the studio's brand.ts.

## 3. Images (`W/brand/`)
In own/website mode, use the user's logo files and generate only what's missing. In match mode, generate everything. Use `python3 "$T/imagegen.py" "<prompt>" <out> --aspect <a>`. Generate, then **look at every result** with Read and regenerate until it is clean.
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
