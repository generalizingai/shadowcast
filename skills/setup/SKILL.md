---
name: setup
description: One-time shadowcast setup check. Verifies tools, API keys, the YouTube OAuth client and disk space, and fixes what it can. Use when someone installs shadowcast or a run fails on a missing dependency or key.
---

# shadowcast setup

**Windows note:** Claude Code on Windows runs commands in Git Bash. If `python3` isn't found, use `python` (or `py`) for every `python3` command in Shadowcast's skills. Paths work with forward slashes.

`T="${CLAUDE_PLUGIN_ROOT}/tools"`

1. Run `python3 "$T/doctor.py"` and show the user the result.
2. Fix what you safely can, one at a time, and say what you're doing:
   - Missing python packages: `python3 -m pip install --user <pkg>`.
   - Cut-out tool:
     - macOS: `zsh "$T/build_cutout.sh"`. It needs the Xcode command line tools; if `swiftc` is missing, tell the user to run `xcode-select --install`.
     - Windows: `python -m pip install --user "rembg[cpu]"`.
   - Windows also needs `python -m pip install --user tzdata`.
   - ffmpeg / yt-dlp / node: give the install line from doctor (`brew` on macOS, `winget` on Windows). Install only if the user agrees.
3. Things only the user can do (explain each in plain steps, then wait):
   - **API keys.** Required: ElevenLabs (voice-over) and Gemini (video analysis and images). Optional: OpenAI and SocialBunny.
     - The user runs `python3 "$T/keys.py" set <name>` in their own terminal. Input is hidden and saved to `~/.config/shadowcast/keys.json` with mode 600.
     - Never ask for a key in chat, never echo one, and never write one into a project file.
     - `python3 "$T/keys.py" list` shows which keys are set.
   - **YouTube OAuth client** (once per person, free):
     1. console.cloud.google.com → new project.
     2. Enable "YouTube Data API v3".
     3. Configure the OAuth consent screen as External, then click **Publish app** (a testing-mode app shows "Access blocked" for other accounts and its tokens expire weekly).
     4. Credentials → Create OAuth client ID → **Desktop app** → download the JSON to `~/.config/shadowcast/client_secret.json`.
   - **Disk:** 8 GB free or more.
4. Run doctor again until every required item is OK.
