# Studio kit reference

Each channel studio lives at `<workspace>/studio/`. Episode code lives in `src/episodes/<ID>/`, and every episode has the same files:

| file | contents |
|---|---|
| `data.ts` | written by `ep.py new`: `W_` (words) and `S_` (sections) from the episode's `audio/*_tight.json` |
| `shots.tsx` (or `shots1.tsx`, `shots2.tsx`, ...) | `export const SHOTS: ShotDef[]`, the long video |
| `short1.tsx`, `short2.tsx` | `export const PREFIX1 = "<section prefix>"`, `export const Short1: React.FC = () => <VShort ... prefix="<same>" .../>` |
| `thumbs.tsx` | `export const ThumbA/ThumbB/ThumbC: React.FC` |
| `index.tsx` | `makeEpisode(...)` and the `EpisodeEntry` with ids `<ID>`, `<ID>Short1`, `<ID>Short2`, `<ID>ThumbA`, ... |

Copy the pattern exactly from `${CLAUDE_PLUGIN_ROOT}/studio-template/src/episodes/_demo/`. Import paths from an episode folder are `../../kit/...`.

## Shots

```tsx
{ at: "first words of the beat", sfx: "thud", marks: ["later word", "another phrase"], msfx: [null, "ding"], el: ({ dur, m }) => (...) }
```
- `at`: the phrase that starts the shot. Matching is case- and punctuation-insensitive and searches forward from the previous shot. `""` means time 0.
  - Pick 2-4 distinctive words. A common word like "the" can match too early.
- `marks`: phrases inside the beat. `m[i]` is the frame (relative to the shot) where that phrase is spoken. Use them so every reveal lands on its word.
- **Write keys in exactly this order on one line: `at`, `sfx`, `marks`.** `tools/audit_layout.py` parses that form.
- `dur`: the shot length in frames. Pass it to `<Photo dur={dur}>` for the slow push.
- SFX are opt-in, about 3-6 per minute: `whoosh pop click thud thunder ding typing riser tick`.
  - Use `click` on countdown/chapter openers, `thud` or `ding` on a big number or verdict.
  - Use no SFX on sad or serious beats.
- New beat about every 4-8 s. Never let one static shot run more than about 10 s; split it, or add marks that reveal more.
- Spoken years ("twenty twenty three", "nineteen eighty nine") become digits in captions automatically. For other spoken-number fixes, pass `fixes={[[["two","point","oh","seven","billion"], "$2.07 billion"]]}` to VShort.

## Canvas and coordinates
- Long video: 1920x1080.
  - Top 110 px: the corner bug (logo + name, top-left) and the rail (top-right). Keep text out of y < 120.
  - `Big`, `Kicker`, `Fact`, `Stamp`, `Money`, `TitleChip`: `y` is an offset from the vertical centre (so -300 is upper). `x` is an offset from the horizontal centre.
- `Star` (cut-out person):
  - `x` is the horizontal centre in px; `y` is the top edge; `h` is the height.
  - Feet/bottom sit at `y + h`. Use `y + h >= 1080` so cut-outs touch the bottom.
  - The name tag sits 70 px above the bottom.
- Short (`VShort`, 1080x1920):
  - Content lives between y ≈ 260 and y = 1420. Captions own y 1440-1520. Below that is the platform UI.
  - `STAR_Y(h)` gives the `y` that puts a cut-out's bottom at 1420. `VW = 1080`, so use `x={VW / 2}`.
  - Text offsets are from the centre (y 960). Typical stack: title at -600, number at -350, star below.
- Thumbnail: 1280x720. Faces are `{src, x (centre), y (top), h}`. Text sits bottom-centre at `tx`. Test that it reads at 320 px wide.

## Components (import from `../../kit/<file>`)

**stage.tsx** (backgrounds; wrap every shot in one):
- `Glam {photo?, photoOp?, dim?, glitter?}`: dark spotlight stage, optionally with a blurred photo.
- `Photo {src, dur, dark?, blur?, zoom?, pan?, pos?, mono?}`: full-bleed real photo with a slow push.
- `Flash {at?}`: flashbulb burst.
- `Bug` is drawn automatically.

**parts.tsx**:
- `Big {text, at, size, y, x, serif, color, maxW}`: huge statement. `*words*` render in the accent; `\n` breaks the line.
- `Kicker {text, at, y, size}`: small accent line with rules.
- `Fact {kick?, lines[], ats?, size, y, align}`: stacked facts that pop in on marks.
- `Stamp {text, sub?, at, y, color, size, rot}`: slammed rubber stamp. Red by default; pass `color={L.gold}` for good news.
- `Money {to, fmt?, at, size, y, label, dur?}`: counting number. Use `fmt={(v) => \`$${Math.round(v)}M\`}`.
- `Star {src, x, y, h, at, from, name, role, flip, glow, sil}`: person cut-out with name tag. `sil` shows a silhouette.
- `Countdown {n, name, role, cut, m}`: countdown item opener with a giant numeral and the person.
- `TitleChip {t, yr?, kind?, at, y, size}`: film/show/book/album title as typography, never artwork.
- `Verdict {title?, rows:[{k, v, c?, at}]}`: outcome table (CHARGED / ACQUITTED ...).
- `QuoteCard {q, who, at}`: ONLY for verbatim, sourced quotes.
- `News {outlet, title, date, hl?, hlAt?, at}`: rebuilt headline. Use the EXACT real headline.
- `Doc {head, sub?, lines[], hlLine?, hlAt?, note}`: recreated document, always labelled.
- `Chips {items[], ats[]}`: small labels row.
- `Slash {at, x, y}`: red X over something.
- `Pic {src, x, y, w, h, cap?}`: framed photo.

**charts.tsx**:
- `TitleCard {kicker?, title, sub?}`, `EndCard {line?}`.
- `ChapterCard {n, title}`; `ChapterTag` is automatic with `rail: "chapters"`.
- `Trio {cols:[{face, who, what}], m, hot?}`
- `Contract {head, clauses:[{t, at}], stamp?}`
- `Timeline {stops:[{label, sub?, at}]}`
- `LockGrid {items[], owner, unlockAt?, unlockOwner?}`
- `Switch {header, rows:[a, b]}`
- `Bars {title, data:[{t, v, sub?}], ats, fmt?, hot?}`: vertical bars, labels nowrap.
- `Stacked {title, segs:[{t, v, label}], ats}`
- `Climb {title, pts:[{d, v, label}], ats, max, ticks?, ref?}`
- `Leaderboard {title, rows:[{name, v, label, face?}], ats}`
- `Choices {question, items[], ats}`: comment bait.

**story.tsx**:
- `Lineup {faces[], revealAt?}`: cold-open row of people.
- `Teasers {items[], m}`: one line at a time.
- `FileStack {labels[], stamp}`
- `PriceTag {from, fromSub, to?, toSub?, swap?}`
- `Versus {a, b, m}`
- `Calendar {month, day, ring?}`
- `Memorial {name, line}`: for deaths. No photo, no SFX.
- `Grid {items:[{face, badge}]}`: outro recap.

**thumb.tsx**: `Thumb {faces[], l1, l2, l2c?, num?, photo, circle?, arrow?, s1, s2, tx}`.

**vshort.tsx**: `VShort {words, sections, prefix, shots, fixes?, endLine?}`. The end line defaults to "FULL VIDEO ON *<BRAND>*".

Colours: `import { L } from "../../kit/theme"`. Use `L.gold` / `L.gold2` (accent), `L.ivory`, `L.red`, `L.green` or `L.dim`. Never hard-code the reference channel's colours.

## When the kit lacks something
Build the new component in `studio/src/kit/extra.tsx`, using the kit's style: `useCurrentFrame`, `pop`/`ease` from `pieces.ts`, and `L`/`LFF`.
- It must work at both 1920x1080 and 1080x1920 (`useVideoConfig`).
- Keep text `whiteSpace: "nowrap"` with a fixed line height wherever alignment matters.
