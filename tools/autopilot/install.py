#!/usr/bin/env python3
"""Install / remove / check the scheduled job that runs autopilot for a channel.

  install.py <slug> [--every-hours 3]
  install.py <slug> --remove
  install.py <slug> --status
macOS: a launchd agent (~/Library/LaunchAgents/com.shadowcast.<slug>.plist).
Windows: a Task Scheduler task "Shadowcast-<slug>" that runs while you're logged in.
The computer must be awake for ticks to run; a missed tick runs at the next interval.
"""
import argparse, os, plistlib, re, subprocess, sys

RUN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run.py")


def mac(a, home):
    label = f"com.shadowcast.{a.slug}"
    path = os.path.expanduser(f"~/Library/LaunchAgents/{label}.plist")
    uid = os.getuid()
    if a.status:
        r = subprocess.run(["launchctl", "print", f"gui/{uid}/{label}"], capture_output=True, text=True)
        return print("installed" if r.returncode == 0 else "not installed")
    subprocess.run(["launchctl", "bootout", f"gui/{uid}/{label}"], capture_output=True)
    if a.remove:
        if os.path.exists(path):
            os.remove(path)
        return print("removed")
    plist = {"Label": label, "ProgramArguments": [sys.executable, RUN, a.slug, "--home", home], "StartInterval": int(a.every_hours * 3600),
             "RunAtLoad": True, "EnvironmentVariables": {"HOME": os.path.expanduser("~")},
             "StandardOutPath": os.path.join(home, a.slug, "scheduler.out"), "StandardErrorPath": os.path.join(home, a.slug, "scheduler.err")}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        plistlib.dump(plist, fh)
    subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", path], check=True)
    print(f"autopilot installed for {a.slug}: every {a.every_hours} h ({path})")


def windows(a, home):
    name = f"Shadowcast-{a.slug}"
    if a.status:
        r = subprocess.run(["schtasks", "/Query", "/TN", name], capture_output=True, text=True)
        return print("installed" if r.returncode == 0 else "not installed")
    subprocess.run(["schtasks", "/Delete", "/TN", name, "/F"], capture_output=True)
    if a.remove:
        return print("removed")
    py = sys.executable.replace("python.exe", "pythonw.exe") if sys.executable.endswith("python.exe") else sys.executable  # no console window
    cmd = f'"{py}" "{RUN}" {a.slug} --home "{home}"'
    hours = max(1, round(a.every_hours))
    subprocess.run(["schtasks", "/Create", "/TN", name, "/TR", cmd, "/SC", "HOURLY", "/MO", str(hours), "/F"], check=True)
    subprocess.run(["schtasks", "/Run", "/TN", name], capture_output=True)
    print(f"autopilot installed for {a.slug}: every {hours} h (Task Scheduler: {name})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug"); ap.add_argument("--every-hours", type=float, default=3); ap.add_argument("--remove", action="store_true"); ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,40}", a.slug):
        sys.exit("bad slug")
    home = os.path.abspath(os.path.expanduser(os.environ.get("SHADOWCAST_HOME", "~/Shadowcast")))
    if sys.platform == "darwin":
        mac(a, home)
    elif os.name == "nt":
        windows(a, home)
    else:
        sys.exit(f"Linux: add this to `crontab -e` instead:\n0 */{max(1, round(a.every_hours))} * * * {sys.executable} {RUN} {a.slug} --home {home}")


if __name__ == "__main__":
    main()
