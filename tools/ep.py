#!/usr/bin/env python3
"""Episode lifecycle for a channel workspace.

  ep.py new <slug> "<working title>"       -> episodes/<NN-slug>/ + studio/src/episodes/<ID>/ stubs; prints the folder
  ep.py register <slug> <ID>               add the episode to the studio registry (after its shots exist)
  ep.py set <slug> <ID> <status> [k=v...]  update meta.json status (+ fields)
  ep.py list <slug>                        every episode with status
  ep.py next <slug>                        the next action autopilot should take (JSON)

Statuses, in order: planned, researched, scripted, awaiting_approval, approved, voiced, built, audited, rendered,
packaged, scheduled. Rejected scripts go back to "researched" with a `feedback` note.
Approval: channel.json approval.mode = "off" | "optional" | "required". "optional" auto-approves after window_hours
unless the user objected; real_people channels always wait for /approve (defamation risk).
"""
import datetime as dt, json, os, re, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from forge import PLUGIN, channel, channel_dir  # noqa: E402

ORDER = ["planned", "researched", "scripted", "awaiting_approval", "approved", "voiced", "built", "audited", "rendered", "packaged", "scheduled"]
NOW = lambda: dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def episodes(slug):
    root = os.path.join(channel_dir(slug), "episodes")
    out = []
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d, "meta.json")
        if os.path.exists(p):
            m = json.load(open(p)); m["_dir"] = os.path.join(root, d); out.append(m)
    return out


def find(slug, eid):
    for m in episodes(slug):
        if m["id"] == eid:
            return m
    sys.exit(f"no episode {eid} in {slug}")


def save(m):
    d = m.pop("_dir")
    json.dump(m, open(os.path.join(d, "meta.json"), "w"), indent=1, ensure_ascii=False)
    m["_dir"] = d


def new(slug, title):
    c = channel(slug); root = channel_dir(slug)
    eps = episodes(slug)
    n = max([int(re.sub(r"\D", "", m["id"]) or 0) for m in eps] + [0]) + 1
    eid = f"{c['code']}{n:02d}"
    words = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-").split("-")
    d = os.path.join(root, "episodes", f"{n:02d}-{'-'.join(words[:5])}")
    for sub in ("audio", "assets/web", "assets/cut", "assets/brand", "assets/audio", "out"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    for f in os.listdir(os.path.join(PLUGIN, "studio-template/demo-episode/assets/audio")):
        shutil.copy(os.path.join(PLUGIN, "studio-template/demo-episode/assets/audio", f), os.path.join(d, "assets/audio"))
    for f in ("wordmark.png", "mono.png"):
        if os.path.exists(os.path.join(root, "brand", f)):
            shutil.copy(os.path.join(root, "brand", f), os.path.join(d, "assets/brand"))
    for f in ("FACTSHEET.md", "SCRIPT.md"):
        shutil.copy(os.path.join(PLUGIN, "templates", f), d)
    # placeholder timing so the studio type-checks before the VO exists (tts.py overwrites these)
    for f in ("words_tight.json", "sections_tight.json"):
        p = os.path.join(d, "audio", f)
        if not os.path.exists(p):
            json.dump([{"w": "placeholder", "s": 0, "e": 1}] if f.startswith("words") else [{"name": "COLD OPEN", "s": 0, "e": 1}], open(p, "w"))
    src = os.path.join(root, "studio/src/episodes", eid); os.makedirs(src, exist_ok=True)
    rel = f"../../../../episodes/{os.path.basename(d)}/audio"
    stub = {
        "data.ts": f'import words from "{rel}/words_tight.json";\nimport sections from "{rel}/sections_tight.json";\n'
                   'import type { Word } from "../../kit/timing";\nimport type { Section } from "../../kit/episode";\n\n'
                   "export const W_ = words as Word[];\nexport const S_ = sections as Section[];\n",
    }
    for f, s in stub.items():
        open(os.path.join(src, f), "w").write(s)
    m = {"id": eid, "title": title, "status": "planned", "created": NOW(), "history": [["planned", NOW()]]}
    json.dump(m, open(os.path.join(d, "meta.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps({"id": eid, "dir": d, "src": src}))


def register(slug, eid):
    p = os.path.join(channel_dir(slug), "studio/src/episodes/index.ts")
    s = open(p).read()
    if f'from "./{eid}"' in s:
        return print("already registered")
    s = s.replace("export const EPISODES", f'import {eid.lower()} from "./{eid}";\n\nexport const EPISODES', 1)
    s = re.sub(r"(EPISODES: EpisodeEntry\[\] = \[)", rf"\1\n  {eid.lower()},", s, 1)
    open(p, "w").write(s)
    print(f"registered {eid}")


def set_status(slug, eid, status, kv):
    if status not in ORDER:
        sys.exit(f"status must be one of {ORDER}")
    m = find(slug, eid)
    m["status"] = status
    m.setdefault("history", []).append([status, NOW()])
    if status == "awaiting_approval":
        m["approval_requested"] = NOW()
    for x in kv:
        k, v = x.split("=", 1)
        m[k] = v
    save(m)
    print(f"{eid} -> {status}")


def approval_state(c, m, first=False):
    """'approved' | 'waiting' | 'rejected' for an episode in awaiting_approval. The channel's first episode always waits."""
    if m.get("feedback"):
        return "rejected"
    ap = c.get("approval", {})
    mode = ap.get("mode", "optional")
    if mode == "off" and not first:
        return "approved"
    if mode == "required" or c.get("real_people") or first:
        return "waiting"
    asked = dt.datetime.fromisoformat(m["approval_requested"])
    return "approved" if dt.datetime.now(dt.timezone.utc) - asked >= dt.timedelta(hours=float(ap.get("window_hours", 12))) else "waiting"


def next_action(slug):
    """What autopilot should do now: finish the most advanced unfinished episode first, then keep `episodes_ahead` booked."""
    c = channel(slug)
    eps = episodes(slug)
    open_eps = [m for m in eps if m["status"] != "scheduled"]
    first = not any(m["status"] == "scheduled" for m in eps)
    for m in sorted(open_eps, key=lambda m: -ORDER.index(m["status"])):
        if m["status"] == "awaiting_approval":
            st = approval_state(c, m, first)
            if st == "approved":
                return {"action": "auto_approve", "id": m["id"], "dir": m["_dir"]}
            if st == "rejected":
                return {"action": "rewrite_script", "id": m["id"], "dir": m["_dir"], "feedback": m["feedback"]}
            continue  # waiting: work on something else meanwhile
        return {"action": "continue_episode", "id": m["id"], "dir": m["_dir"], "status": m["status"]}
    import publish.slots as slots  # noqa: E402
    booked = slots.upcoming(slug)
    if len(booked) + len(open_eps) < int(c.get("episodes_ahead", 2)):
        return {"action": "new_episode"}
    return {"action": "idle", "booked": booked, "waiting": [m["id"] for m in open_eps]}


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmd = a[0]
    if cmd == "new" and len(a) == 3:
        new(a[1], a[2])
    elif cmd == "register" and len(a) == 3:
        register(a[1], a[2])
    elif cmd == "set" and len(a) >= 4:
        set_status(a[1], a[2], a[3], a[4:])
    elif cmd == "list" and len(a) == 2:
        for m in episodes(a[1]):
            print(f"{m['id']:6s} {m['status']:18s} {m.get('release', ''):11s} {m['title']}")
    elif cmd == "next" and len(a) == 2:
        print(json.dumps(next_action(a[1])))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
