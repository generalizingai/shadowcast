# Production rules

These are lessons from shipped episodes. Each one fixed a real, visible mistake, so treat them as hard rules.

## Truth and legal (real-people channels)
- The script may only say what FACTSHEET.md supports. Give every claim its exact status: alleged, charged, acquitted, settled, dropped, reported, estimated. "Acquitted" must never become "got away with it".
- Never invent a quote. Quote marks are only for verbatim, sourced words. Paraphrases go without quote marks, and on screen only as plain text or `Doc` with `note="PARAPHRASED"`.
- `News` cards use the exact real headline, outlet and date. Never make one up.
- No AI-generated images of real people. People are real, freely licensed photos (Wikimedia Commons) cut out with the cutout tool, or silhouettes.
- No movie stills, posters, album covers, TV screenshots or logos as imagery. Titles appear as typography (`TitleChip`).
- Deaths and victims get weight: use `Memorial`, no SFX, no jokes, no "shocking" framing. Skip stories whose core is the assault of a living victim.
- Money: say what a figure is (gross vs profit, estimate vs reported). Net worth is "estimated by Forbes/Bloomberg".
- When unsure, cut the claim. An accurate video that's 30 s shorter beats a takedown.

## Script
- Hook in the first 5 s: the most surprising true thing, said plainly. No "welcome back".
- Every countdown item or chapter needs a turn: setup, then twist, then consequence.
- Write for the ear: short sentences, numbers as words, one idea per sentence.
- Target length = `format.minutes` × `format.wpm` words, ±5%.
- End with the comment-bait question and a one-line subscribe CTA. No long sign-off.

## Layout (the busiest-frame audit)
Short-interval contact sheets miss layout bugs, because elements build up during a shot. `tools/audit_layout.py` renders the LAST frame of every shot, when everything is on screen. Open every sheet with Read and check each frame for:
- text crossing a frame edge or clipped (long words at large sizes, numbers with many digits)
- text over a face, or a kicker sitting on someone's head or cap
- two elements overlapping (a stamp on a chart, a number on a name tag, a leader line through a label)
- anything inside the bug/rail zone (y < 120 on long videos) or inside the Shorts caption band / below y = 1420
- a chart label that wrapped to two lines. That shifts bars off a shared baseline, so use shorter labels.
- a missing image (broken asset path) or an empty frame
- the same layout repeated more than 3 times in a row (vary it)

Fix every issue, re-run the audit, and look again. Do not render until a full sheet set is clean.

## Shorts
- Two per episode: Short 1 is the strongest hook beat, Short 2 is the #1 or payoff beat. Each comes from one VO section, ideally 35-60 s.
- Native 9:16 built from the section with `VShort` and its own shots. Never a boxed 16:9 frame.
- Captions are small (58 px) in their own band. Nothing else goes there.
- Titles stay under 70 characters and end with `#shorts`.

## Thumbnails
- Make 2-3 variants (ThumbA/B/C). Use 1-3 tight faces of the real people (cut-outs) and at most 2 text lines, 2-4 words each, huge and high-contrast.
- One accent: a circle, arrow or number. Check it reads at 320 px wide.
- A thumbnail can't promise anything the video doesn't deliver.

## Assets
- Photos come from `commons.py search` / `fetch` (Wikimedia via the en.wikipedia API). Keys and naming:
  - `b_<name>.jpg` for backgrounds.
  - `p_<name>.jpg` for people. Then cut out with `cutout.py web/p_<name>.jpg cut/<name>.png`.
- Every fetch appends to `assets/web/CREDITS.md`. Credits are computed from what the shots actually reference, so reference assets by literal path strings (`"web/b_x.jpg"`, `"cut/x.png"`).
- Commons rate-limits with 429s. Start building shots with stand-ins (`Glam`, silhouettes) while photos download; never sit idle.
- Look at every cut-out before using it. Reject bad masks, other people's limbs, logos, and watermarks.
- AI images (`imagegen.py`) are only for non-person scenery, textures, objects and backgrounds, and only where the style allows. They need no credit line.

## Render
- Renders need about 3 GB of free temp space. Check free disk space first.
- Long: `render.py episode <slug> <ID> long`. Shorts render with concurrency 2, because they eat memory.
- After rendering, check `ffprobe` duration, and view 6 frames spread across the long video plus 3 per Short.
- Audio is normalised to -14 LUFS.
