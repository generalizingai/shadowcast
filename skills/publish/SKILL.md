---
name: publish
description: Schedule a packaged shadowcast episode on YouTube (long video plus 2 Shorts, with thumbnail), and optionally on Facebook and Instagram through SocialBunny, using the channel's release calendar. Also YouTube auth and channel branding. Use for "schedule/publish episode X", "connect YouTube" or "set the banner".
argument-hint: <channel slug> <episode ID> | auth <slug> | brand <slug>
---

# Publish

`T="${CLAUDE_PLUGIN_ROOT}/tools"`, `P="$T/publish/publish.py"`, `W="${SHADOWCAST_HOME:-$HOME/Shadowcast}/<slug>"`.
Nothing is ever published immediately:
- YouTube uploads are **private with a publishAt time**, and YouTube makes them public on schedule.
- SocialBunny posts get a future `scheduledAt`.
- `publish.state.json` records every upload, so re-running is always safe.

## Connect YouTube (once per channel; the user must click through Google consent)
`python3 "$P" auth <slug>` opens a browser on port 8765.
- Tell the user to pick the **new channel's** Brand Account, not their personal channel.
- Then run `python3 "$P" whoami <slug>`, and save that exact title as `youtube.channel_title` in channel.json.

## Apply branding (after auth)
Run:
```
python3 "$P" brand <slug> --banner "$W/brand/banner.jpg" --description-file "$W/brand/description.txt" --keywords "<comma list from channel.json youtube.keywords>"
```
The API can't change the channel **name** or **profile picture**. Give the user `W/brand/avatar.png` and the name, with the Studio path: YouTube Studio → Customization → Branding / Basic info.

## Schedule an episode
1. Make sure the status is `packaged` (`python3 "$T/ep.py" list <slug>`).
2. `python3 "$P" schedule "<dir>/out/publish.json"` books the next free release day and prints the local times. Pass `--date YYYY-MM-DD` only if the user asked for a date.
3. `python3 "$P" publish "<dir>/out/publish.json" --dry-run`, then show the plan.
4. `python3 "$P" publish "<dir>/out/publish.json"` uploads with resume and retries; this takes several minutes per video.
   - Thumbnail upload fails with 403 until the channel is phone-verified (youtube.com/verify). Tell the user once; re-running later sets it.
5. `python3 "$P" comment "<dir>/out/publish.json"` posts the photo-credit comment on the long video. Ask the user to pin it in Studio.
6. Run `python3 "$T/ep.py" set <slug> <ID> scheduled release=<date>`, then `python3 "$T/notify.py" <slug> "Scheduled <ID>" "<title> goes live <day time>"`.
7. Report the YouTube links and times.

## Facebook / Instagram (optional)
These only run when `channel.json social.socialbunny` is set to `{"facebook": "<page handle>", "instagram": "<handle>", "fb_reels": true}` and the `socialbunny_api_key` key is set (`keys.py set socialbunny_api_key`).
- Check the accounts with `python3 "$P" accounts <slug>`. Long video goes to Facebook; Shorts go to Facebook and Instagram as Reels, at the same times.

## Errors
- "token is for 'X', manifest wants 'Y'": the wrong channel was authorised. Re-run auth and pick the right one.
- "Access blocked" in consent: the user's Google Cloud app is still in Testing. Publish it (see the setup skill).
- quotaExceeded: the YouTube API allows about 6 uploads a day per project. Wait 24 h; the next run resumes.
