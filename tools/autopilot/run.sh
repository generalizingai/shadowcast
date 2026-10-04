#!/bin/zsh
# One autopilot tick for one channel (launchd runs this; safe to run by hand).
#   run.sh <slug>
# Runs Claude Code headless with the shadowcast autopilot skill. Uses your logged-in Claude subscription.
# A lock stops overlapping ticks (a full episode build can take a few hours).
SLUG=$1
[[ "$SLUG" =~ ^[a-z0-9][a-z0-9-]{1,40}$ ]] || { echo "bad slug" >&2; exit 2; }
HOMEF=${SHADOWCAST_HOME:-$HOME/Shadowcast}; LOG="$HOMEF/$SLUG/autopilot.log"; LOCK="$HOMEF/$SLUG/.autopilot.lock"
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"
if ! mkdir "$LOCK" 2>/dev/null; then
  # stale lock (machine slept or crashed) after 8 h
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +480)" ]; then rmdir "$LOCK"; mkdir "$LOCK"; else echo "$(date) busy, skipping" >> "$LOG"; exit 0; fi
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT
cd "$HOMEF/$SLUG" || exit 1
echo "=== $(date) tick" >> "$LOG"
claude -p "/shadowcast:autopilot $SLUG" \
  --model "${SHADOWCAST_MODEL:-claude-opus-5-5}" \
  --permission-mode acceptEdits \
  --allowedTools "Bash(python3:*)" "Bash(node:*)" "Bash(npx remotion:*)" "Bash(zsh:*)" "Bash(ffmpeg:*)" "Bash(ffprobe:*)" "Bash(curl:*)" "Bash(ls:*)" "Bash(mkdir:*)" "Bash(cp:*)" "Bash(mv:*)" "Bash(df:*)" "Bash(cat:*)" "Read" "Write" "Edit" "Glob" "Grep" "WebSearch" "WebFetch" "Skill" \
  >> "$LOG" 2>&1
echo "=== $(date) done ($?)" >> "$LOG"
