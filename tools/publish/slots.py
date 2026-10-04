"""Release calendar per channel, from channel.json "schedule":
  {"tz": "America/New_York", "days": ["Mon","Wed","Fri"], "lead_hours": 3,
   "slots": {"long": [0, "18:00"], "short1": [0, "18:30"], "short2": [1, "11:00"]}}
Each slot is [days after release day, local time]. Same times on every platform. DST is handled by the time zone.
<workspace>/<slug>/calendar.json maps episode -> release date so a day is never double-booked."""
import datetime as dt, json, os, sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import channel, channel_dir  # noqa: E402

WD = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def rules(slug):
    s = channel(slug)["schedule"]
    tz = ZoneInfo(s.get("tz", "America/New_York"))
    days = [WD.index(d[:3].title()) for d in s["days"]]
    slots = {r: (int(off), *map(int, t.split(":"))) for r, (off, t) in s["slots"].items()}
    return tz, days, slots, float(s.get("lead_hours", 3))


def _cal(slug):
    return os.path.join(channel_dir(slug), "calendar.json")


def load_cal(slug):
    p = _cal(slug)
    return json.load(open(p)) if os.path.exists(p) else {}


def times_for(slug, date):
    tz, _, slots, _ = rules(slug)
    return {r: dt.datetime.combine(date + dt.timedelta(days=off), dt.time(h, m), tzinfo=tz).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            for r, (off, h, m) in slots.items()}


def next_free(slug, episode):
    cal = load_cal(slug)
    if episode in cal:
        return dt.date.fromisoformat(cal[episode])
    tz, days, slots, lead = rules(slug)
    _, h, m = slots["long"]
    taken, now = set(cal.values()), dt.datetime.now(tz)
    d = now.date()
    while True:
        if d.weekday() in days and d.isoformat() not in taken and dt.datetime.combine(d, dt.time(h, m), tzinfo=tz) - now >= dt.timedelta(hours=lead):
            return d
        d += dt.timedelta(days=1)


def book(slug, episode, date):
    _, days, _, _ = rules(slug)
    if date.weekday() not in days:
        raise SystemExit(f"{date} is not a release day for {slug}")
    cal = load_cal(slug)
    other = [e for e, v in cal.items() if v == date.isoformat() and e != episode]
    if other:
        raise SystemExit(f"{date} is already booked by {other[0]}")
    cal[episode] = date.isoformat()
    json.dump(dict(sorted(cal.items(), key=lambda kv: kv[1])), open(_cal(slug), "w"), indent=1)


def upcoming(slug):
    today = dt.date.today().isoformat()
    return sorted(e for e, d in load_cal(slug).items() if d >= today)
