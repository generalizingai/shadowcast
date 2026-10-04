#!/usr/bin/env python3
"""Install / remove the macOS launchd job that runs autopilot for a channel.

  install.py <slug> [--every-hours 3]     load ~/Library/LaunchAgents/com.channelforge.<slug>.plist
  install.py <slug> --remove
  install.py <slug> --status
The Mac must be awake (and logged in) for ticks to run; missed ticks run at the next wake.
"""
import argparse, os, plistlib, re, subprocess, sys

RUN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run.sh")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug"); ap.add_argument("--every-hours", type=float, default=3); ap.add_argument("--remove", action="store_true"); ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,40}", a.slug):
        sys.exit("bad slug")
    label = f"com.channelforge.{a.slug}"
    path = os.path.expanduser(f"~/Library/LaunchAgents/{label}.plist")
    uid = os.getuid()
    if a.status:
        r = subprocess.run(["launchctl", "print", f"gui/{uid}/{label}"], capture_output=True, text=True)
        print("installed" if r.returncode == 0 else "not installed")
        return
    subprocess.run(["launchctl", "bootout", f"gui/{uid}/{label}"], capture_output=True)
    if a.remove:
        if os.path.exists(path):
            os.remove(path)
        print("removed")
        return
    home = os.path.expanduser(os.environ.get("FORGE_HOME", "~/ChannelForge"))
    plist = {"Label": label, "ProgramArguments": ["/bin/zsh", RUN, a.slug], "StartInterval": int(a.every_hours * 3600), "RunAtLoad": True,
             "EnvironmentVariables": {"FORGE_HOME": home, "HOME": os.path.expanduser("~")},
             "StandardOutPath": os.path.join(home, a.slug, "launchd.out"), "StandardErrorPath": os.path.join(home, a.slug, "launchd.err")}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        plistlib.dump(plist, fh)
    subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", path], check=True)
    print(f"autopilot installed for {a.slug}: every {a.every_hours} h ({path})")


if __name__ == "__main__":
    main()
