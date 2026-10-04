---
name: clone-channel
description: The full shadowcast flow. Give it a YouTube channel link and it audits the channel, learns its format, creates an original channel identity (name, logo, banner, voice), connects YouTube, produces and schedules the first episode with 2 Shorts and thumbnails, then turns on autopilot for hands-free videos on a schedule. Use when someone pastes a channel link and wants their own channel "like this one".
argument-hint: <youtube channel url or @handle>
---

# Clone a channel's format into a new, original channel

`T="${CLAUDE_PLUGIN_ROOT}/tools"`, `H="${SHADOWCAST_HOME:-$HOME/Shadowcast}"`.

We copy what makes a channel work: format, pacing, visual grammar, look (palette, font feel, thumbnail style), packaging and cadence. The **identity** is the user's: their brand files or website if they gave them, otherwise an original name, logo, avatar and banner styled like the reference. Never copy the reference channel's name, logo, avatar or banner (YouTube terminates impersonating channels), and never reuse its videos, thumbnails or scripts. Say this once to the user.

Keep the user informed with one short line per milestone. Ask the user only where marked **[user]**; everything else is automatic.

## 0. Ready check
Run `python3 "$T/doctor.py"`. If any required item is missing, run the setup skill first, then come back.

## 1. Audit (about 10 min)
Follow the channel-audit skill steps 1-4 with `A="$H/_audits/<handle>"`.

## 2. Identity
0. **[user]** Ask once: "Do you have your own branding (a folder of logo and colour files) or a website I should take it from? If not, I'll match the reference channel's look with an original name and logo." The answer sets `brand.source`: own / website / match.
1. Name + handle:
   - own/website: take them from the user or site.
   - match: follow brand-kit step 1. **[user]** If the user is present, let them pick from 4 names.
2. Create the workspace: `python3 "$T/new_channel.py" <slug> --name "<Name>" --code <XX> --source "<url>"`.
   - The slug is the name lowercased with dashes. The first run installs Remotion once (~300 MB).
3. Move the audit in: `mv "$H/_audits/<handle>" "$H/<slug>/audit"`.
4. Finish channel-audit steps 5-6 (STYLE.md and channel.json).
5. Finish brand-kit steps 0 and 2-5 (brand source, look, images, voice, description).
6. **[user]** Ask only if unknown:
   - Release days and times. Default: Mon/Wed/Fri; long video 6 PM, Short 1 6:30 PM, Short 2 11 AM next day, in the user's time zone.
   - Approval mode. Default `optional` with a 12 h window. Real-people channels always wait.
   - Facebook/Instagram via SocialBunny (optional).
   Write the answers to channel.json.

## 3. Connect YouTube **[user, one time, about 5 min]**
The YouTube API cannot create channels or set a channel's name or picture, so give the user this short checklist and wait:
1. youtube.com → profile → Settings → **Add or manage your channels** → **Create a channel**. Name it "<Name>"; this makes a Brand Account.
2. Upload `<H>/<slug>/brand/avatar.png` as the profile picture (Studio → Customization → Branding).
3. Verify the channel at youtube.com/verify (phone). This is needed for custom thumbnails and videos over 15 minutes.
4. Then run (or let Claude run) `python3 "$T/publish/publish.py" auth <slug>` and pick **that** channel in the Google consent screen.
Afterwards: run `whoami`, save `youtube.channel_title`, and apply the banner/description/keywords with the publish skill ("Apply branding").

## 4. First episode
Run the episode skill for `<slug>`, using the top topic from STYLE.md.
- **[user]** The approval gate shows them the script. A first episode always waits for approval, even in optional mode, so the user sees the quality before autopilot runs.
- Then render, package and schedule (publish skill).
- Show the user the long-video and Short contact frames and the thumbnail before publishing.

## 5. Autopilot
**[user]** Offer to turn on autopilot: `python3 "$T/autopilot/install.py" <slug> --every-hours 3`. Explain:
- it keeps `episodes_ahead` episodes (default 2) booked;
- it notifies them when a script needs review;
- the computer needs to be awake.

## Finish
Summarise:
- channel name and handle
- the first video's links and go-live times
- the release calendar
- autopilot status
- where everything lives (`H/<slug>/`)
- the commands: `/shadowcast:episode <slug>`, `/shadowcast:approve <slug> <ID>`, `/shadowcast:autopilot status <slug>`
