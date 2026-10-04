#!/usr/bin/env python3
"""Desktop notification (macOS / Windows) plus a line in <workspace>/<slug>/inbox.md so nothing is lost.
  notify.py <slug> "<title>" "<message>" """
import datetime as dt, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import channel_dir  # noqa: E402

slug, title, msg = sys.argv[1], sys.argv[2][:80], sys.argv[3][:300]
with open(os.path.join(channel_dir(slug), "inbox.md"), "a", encoding="utf-8") as fh:
    fh.write(f"- {dt.datetime.now():%Y-%m-%d %H:%M} **{title}**: {msg}\n")
full = "Shadowcast: " + title
if sys.platform == "darwin":
    subprocess.run(["osascript", "-e", f"display notification {json.dumps(msg)} with title {json.dumps(full)}"], capture_output=True)
elif os.name == "nt":
    q = lambda s: s.replace("'", "''")
    ps = ("Add-Type -AssemblyName System.Windows.Forms; $n = New-Object System.Windows.Forms.NotifyIcon; "
          "$n.Icon = [System.Drawing.SystemIcons]::Information; $n.Visible = $true; "
          f"$n.ShowBalloonTip(10000, '{q(full)}', '{q(msg)}', 'Info'); Start-Sleep -Seconds 11; $n.Dispose()")
    subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps])
