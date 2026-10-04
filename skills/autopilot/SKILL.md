---
name: autopilot
description: One unattended autopilot tick for a shadowcast channel. It does the single most useful next step (continue an episode, auto-approve after the review window, start a new episode, or schedule) and stops. Run by the launchd job via headless Claude Code; also use it to install, remove or check autopilot.
argument-hint: <channel slug> | install <slug> [hours] | remove <slug> | status <slug>
---

# Autopilot

`T="${CLAUDE_PLUGIN_ROOT}/tools"`

## Install / remove / status (interactive)
- Install: `python3 "$T/autopilot/install.py" <slug> --every-hours 3`. This creates a launchd agent on macOS, or a Task Scheduler task on Windows, that runs `tools/autopilot/run.py <slug>`. That script calls `claude -p "/shadowcast:autopilot <slug>" --model claude-opus-5-5` with a fixed tool allowlist, a lock, and a log at `<workspace>/<slug>/autopilot.log`.
- `--remove` and `--status` do what they say.
- Tell the user what this means:
  - The computer must be on and awake. On macOS: System Settings → Energy → prevent sleep when plugged in. On Windows: Settings → Power → Sleep: Never (when plugged in).
  - Each tick uses their Claude subscription.
  - Scripts for real-people channels always wait for `/shadowcast:approve`.
  - Notifications and `<workspace>/<slug>/inbox.md` say when something needs them.

## A tick (headless; there is no user to ask)
Never ask questions or wait for input. If something needs a human, run `python3 "$T/notify.py" <slug> "<title>" "<what to do>"` and end the tick.

1. Run `python3 "$T/ep.py" next <slug>`, then act on the action it returns:
   - `continue_episode`: run the episode skill for that ID from its status. Go as far as possible: research, script, and approval gate, or voice, build, audit, render, package and schedule.
   - `auto_approve`: the review window passed with no objection. Run `python3 "$T/ep.py" set <slug> <ID> approved`, notify "Auto-approved <ID>", then continue the episode.
   - `rewrite_script`: the user gave feedback. Rewrite the script per the episode skill, then go back to `awaiting_approval`.
   - `new_episode`: start the next episode (episode skill, step 1).
   - `idle`: nothing to do. Print one line and stop.
2. Then check for anything packaged but not scheduled, and publish it (publish skill: schedule, then publish, then comment).
3. **Hard stops.** Notify the user and end the tick on any of these:
   - a missing key or expired YouTube token
   - less than 4 GB of free disk
   - a quota error
   - a layout audit you can't get clean after 3 passes
   - a fact you can't source (cut it instead, if you can)
4. End with a 3-line summary of what changed. It goes to the log.
