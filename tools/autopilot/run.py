#!/usr/bin/env python3
"""One autopilot tick for one channel (launchd / Task Scheduler runs this; safe to run by hand).

  run.py <slug> [--home <workspace dir>]
Runs Claude Code headless with the shadowcast autopilot skill on your logged-in Claude subscription.
A lock folder stops overlapping ticks (a full episode build can take hours); a lock older than 8 h is treated as stale.
"""
import datetime as dt, os, re, shutil, subprocess, sys, time

ALLOWED = ["Bash(python3:*)", "Bash(python:*)", "Bash(py:*)", "Bash(node:*)", "Bash(npx remotion:*)", "Bash(ffmpeg:*)", "Bash(ffprobe:*)",
           "Bash(curl:*)", "Bash(ls:*)", "Bash(mkdir:*)", "Bash(cp:*)", "Bash(mv:*)", "Bash(df:*)", "Bash(cat:*)",
           "Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch", "Skill"]


def main():
    a = sys.argv[1:]
    if not a or not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,40}", a[0]):
        sys.exit(__doc__)
    slug = a[0]
    home = a[a.index("--home") + 1] if "--home" in a else os.environ.get("SHADOWCAST_HOME", os.path.expanduser("~/Shadowcast"))
    root = os.path.join(home, slug)
    os.environ["SHADOWCAST_HOME"] = home
    if sys.platform == "darwin":  # launchd starts with a minimal PATH
        os.environ["PATH"] = ":".join(["/opt/homebrew/bin", "/usr/local/bin", os.path.expanduser("~/.local/bin"), os.path.expanduser("~/.npm-global/bin"), os.environ.get("PATH", "")])
    log = open(os.path.join(root, "autopilot.log"), "a", encoding="utf-8")
    lock = os.path.join(root, ".autopilot.lock")
    try:
        os.mkdir(lock)
    except FileExistsError:
        if time.time() - os.path.getmtime(lock) < 8 * 3600:
            log.write(f"{dt.datetime.now():%Y-%m-%d %H:%M} busy, skipping\n"); return
        os.rmdir(lock); os.mkdir(lock)
    try:
        claude = shutil.which("claude") or "claude"
        log.write(f"=== {dt.datetime.now():%Y-%m-%d %H:%M} tick\n"); log.flush()
        r = subprocess.run([claude, "-p", f"/shadowcast:autopilot {slug}", "--model", os.environ.get("SHADOWCAST_MODEL", "claude-opus-5-5"),
                            "--permission-mode", "acceptEdits", "--allowedTools", *ALLOWED], cwd=root, stdout=log, stderr=subprocess.STDOUT)
        log.write(f"=== {dt.datetime.now():%Y-%m-%d %H:%M} done ({r.returncode})\n")
    finally:
        os.rmdir(lock)


if __name__ == "__main__":
    main()
