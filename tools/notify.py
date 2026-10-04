#!/usr/bin/env python3
"""macOS notification (and a line in <workspace>/<slug>/inbox.md so nothing is lost):  notify.py <slug> "<title>" "<message>" """
import datetime as dt, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from forge import channel_dir  # noqa: E402

slug, title, msg = sys.argv[1], sys.argv[2][:80], sys.argv[3][:300]
with open(os.path.join(channel_dir(slug), "inbox.md"), "a") as fh:
    fh.write(f"- {dt.datetime.now():%Y-%m-%d %H:%M} **{title}**: {msg}\n")
script = f"display notification {json.dumps(msg)} with title {json.dumps('Channel Forge: ' + title)}"
subprocess.run(["osascript", "-e", script], capture_output=True)
