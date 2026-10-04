#!/usr/bin/env python3
"""Publisher: one finished episode package -> YouTube (+ optional Facebook/Instagram) on the channel's schedule.

  publish.py auth <slug>                  YouTube consent (pick that channel's Brand Account)
  publish.py whoami <slug>                channel the YouTube token posts to
  publish.py brand <slug> [--banner f] [--description-file f] [--keywords "a,b"]   set banner/description/keywords
  publish.py accounts <slug>              SocialBunny connection ids for the channel's Facebook/Instagram handles
  publish.py schedule <publish.json> [--date YYYY-MM-DD]   book the next free release day (or the given one), stamp times
  publish.py publish <publish.json> [--only youtube,socialbunny] [--dry-run]
  publish.py comment <publish.json>       post the photo-credit comment on the long video (pin it in Studio)
  publish.py queue <slug>                 recent SocialBunny scheduled posts

publish.json carries "channel_slug" (workspace) and "channel" (exact YouTube channel title, checked before upload).
Routing by role: long -> YouTube + Facebook video; short1/short2 -> YouTube Short + Facebook + Instagram Reel.
Facebook/Instagram only when channel.json social.socialbunny is set. Times come from channel.json schedule (slots.py).
Safety: nothing is ever published immediately. YouTube uploads private + publishAt; SocialBunny posts are created
with a future scheduledAt. publish.state.json (next to the manifest) records every upload,
so re-runs never double-post; a changed time on an already-uploaded YouTube video is applied as a reschedule.
"""
import argparse, datetime as dt, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import slots  # noqa: E402
from common import channel  # noqa: E402

# platform group -> SocialBunny targets per role
META = {"long": ["facebook"], "short1": ["facebook", "instagram"], "short2": ["facebook", "instagram"]}
ROUTES = {r: ["youtube", "socialbunny"] for r in META}
SKEY = {"youtube": "{k}", "socialbunny": "sb:{k}"}


def use(slug):
    import yt, socialbunny
    yt.SLUG = socialbunny.SLUG = slug


def load(path):
    base = os.path.dirname(os.path.abspath(path))
    sp = os.path.join(base, "publish.state.json")
    man = json.load(open(path))
    if not man.get("channel_slug"):
        sys.exit("publish.json has no channel_slug")
    use(man["channel_slug"])
    return man, base, sp, (json.load(open(sp)) if os.path.exists(sp) else {})


def save_state(sp, st):
    json.dump(st, open(sp, "w"), indent=1)


def validate(man, base):
    errs = []
    for it in man["youtube"]:
        k = it["key"]
        for f in ("file", "title", "description", "role"):
            if not it.get(f):
                errs.append(f"{k}: missing {f}")
        if it.get("role") not in ROUTES:
            errs.append(f"{k}: role must be one of {list(ROUTES)}")
        if it.get("file") and not os.path.exists(os.path.join(base, it["file"])):
            errs.append(f"{k}: file not found {it['file']}")
        if it.get("thumbnail") and not os.path.exists(os.path.join(base, it["thumbnail"])):
            errs.append(f"{k}: thumbnail not found")
        if len(it.get("title", "")) > 100 or len(it.get("description", "")) > 5000 or len(",".join(it.get("tags", []))) > 500:
            errs.append(f"{k}: title/description/tags over YouTube limits")
        if any(c in it.get("title", "") + it.get("description", "") for c in "<>"):
            errs.append(f"{k}: < or > in title/description")
        if "instagram" in META.get(it.get("role"), []) and len(it.get("social", it.get("description", ""))) > 2200:
            errs.append(f"{k}: social caption over 2200 chars (Instagram limit)")
        if not it.get("publishAt"):
            errs.append(f"{k}: no publishAt (run `publish.py schedule` first)")
    return errs


def due_ok(iso, minutes=15):
    return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")) > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=minutes)


def cmd_schedule(a):
    man, *_ = load(a.manifest)
    ep, slug = man["episode"], man["channel_slug"]
    d = dt.date.fromisoformat(a.date) if a.date else slots.next_free(slug, ep)
    slots.book(slug, ep, d)
    t = slots.times_for(slug, d)
    tz = slots.rules(slug)[0]
    for it in man["youtube"]:
        it["publishAt"] = t[it["role"]]
    man["release"] = d.isoformat()
    json.dump(man, open(a.manifest, "w"), indent=1, ensure_ascii=False)
    print(f"{ep} booked for {d:%a %b %d}:")
    for it in man["youtube"]:
        local = dt.datetime.fromisoformat(it["publishAt"].replace("Z", "+00:00")).astimezone(tz)
        print(f"  {it['role']:6s} {local:%a %b %d %I:%M %p %Z}  {it['title'][:60]}")


def cmd_publish(a):
    man, base, sp, st = load(a.manifest)
    errs = validate(man, base)
    if errs:
        sys.exit("manifest errors:\n  " + "\n  ".join(errs))
    only = set(a.only.split(",")) if a.only else {"youtube", "socialbunny"}
    if not (channel(man["channel_slug"]).get("social") or {}).get("socialbunny"):
        only.discard("socialbunny")
    acc = None
    y = None
    for it in man["youtube"]:
        k, path = it["key"], os.path.join(base, it["file"])
        for plat in ROUTES[it["role"]]:
            if plat not in only:
                continue
            sk = SKEY[plat].format(k=k)
            done = st.get(sk)
            tag = f"{'[dry-run] ' if a.dry_run else ''}{plat:9s} {k}"
            if plat == "youtube":
                if done and done.get("publishAt") == it["publishAt"] and (not it.get("thumbnail") or done.get("thumbnail") == "ok"):
                    print(f"{tag}: up to date https://youtu.be/{done['id']}")
                    continue
                if a.dry_run:
                    print(f"{tag}: {'reschedule/thumbnail' if done else 'upload'} -> {it['publishAt']}")
                    continue
                import yt
                if y is None:
                    y = yt.client()
                    _, name = yt.channel(y)
                    if man.get("channel") and name != man["channel"]:
                        sys.exit(f"YouTube token is for '{name}', manifest wants '{man['channel']}'")
                if not done:
                    if not due_ok(it["publishAt"]):
                        sys.exit(f"{k}: publish time {it['publishAt']} is too close or past; reschedule first")
                    vid = yt.upload(y, it, path, it["publishAt"])
                    done = st[sk] = {"id": vid, "uploaded": dt.datetime.now(dt.timezone.utc).isoformat(), "publishAt": it["publishAt"]}
                    save_state(sp, st)
                    print(f"{tag}: uploaded https://youtu.be/{vid} -> {it['publishAt']}")
                elif done.get("publishAt") != it["publishAt"]:
                    yt.reschedule(y, done["id"], it["publishAt"])
                    done["publishAt"] = it["publishAt"]
                    save_state(sp, st)
                    print(f"{tag}: rescheduled https://youtu.be/{done['id']} -> {it['publishAt']}")
                if it.get("thumbnail") and done.get("thumbnail") != "ok":
                    done["thumbnail"] = yt.set_thumb(y, done["id"], os.path.join(base, it["thumbnail"]))
                    save_state(sp, st)
                    print(f"{tag}: thumbnail {done['thumbnail']}")
                continue
            if done:
                print(f"{tag}: already scheduled ({done.get('id')}) on {', '.join(done.get('targets', []))}")
                continue
            import socialbunny as sb
            if acc is None:
                acc = sb.accounts()
            targets = [p for p in META[it["role"]] if p in acc]
            if a.dry_run:
                print(f"{tag}: {'+'.join(targets)} -> {it['publishAt']}")
                continue
            if not due_ok(it["publishAt"]):
                print(f"{tag}: SKIPPED, publish time {it['publishAt']} too close or past")
                continue
            caption = f"{it['title']}\n\n{it['description']}" if it["role"] == "long" else it.get("social", it["description"])
            url = sb.upload(path)
            pid = sb.schedule(caption, url, it["publishAt"], targets, acc, reel=it["role"] != "long")
            st[sk] = {"id": pid, "targets": targets, "at": dt.datetime.now(dt.timezone.utc).isoformat(), "publishAt": it["publishAt"]}
            save_state(sp, st)
            print(f"{tag}: scheduled post {pid} on {'+'.join(targets)} -> {it['publishAt']}")


def cmd_comment(a):
    man, base, sp, st = load(a.manifest)
    import yt
    done = st.get("long")
    text = man.get("credits_comment")
    if not done or not text:
        sys.exit("needs an uploaded long video and credits_comment in publish.json")
    if done.get("comment"):
        return print("already commented")
    yt.comment(yt.client(), done["id"], text[:9500])
    done["comment"] = "ok"
    save_state(sp, st)
    print(f"commented on https://youtu.be/{done['id']}: pin it in YouTube Studio")


def cmd_brand(a):
    use(a.slug)
    import yt
    desc = open(a.description_file).read().strip() if a.description_file else None
    kw = [k.strip() for k in a.keywords.split(",") if k.strip()] if a.keywords else None
    cid = yt.brand(yt.client(), banner=a.banner, description=desc, keywords=kw)
    print(f"branding updated on {cid}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)

    def yt_auth(a):
        use(a.slug)
        import yt
        print("saved token for channel: %s (%s)" % yt.auth()[::-1])

    def whoami(a):
        use(a.slug)
        import yt
        print("%s (%s)" % yt.channel(yt.client())[::-1])

    def accounts(a):
        use(a.slug)
        import socialbunny as sb
        print(sb.accounts())

    def queue(a):
        use(a.slug)
        import socialbunny as sb
        print(json.dumps(sb.posts(), indent=1)[:4000])

    for name, fn in (("auth", yt_auth), ("whoami", whoami), ("accounts", accounts), ("queue", queue)):
        q = s.add_parser(name); q.add_argument("slug"); q.set_defaults(fn=fn)
    q = s.add_parser("brand"); q.add_argument("slug"); q.add_argument("--banner"); q.add_argument("--description-file"); q.add_argument("--keywords")
    q.set_defaults(fn=cmd_brand)
    q = s.add_parser("schedule"); q.add_argument("manifest"); q.add_argument("--date"); q.set_defaults(fn=cmd_schedule)
    q = s.add_parser("publish"); q.add_argument("manifest"); q.add_argument("--only"); q.add_argument("--dry-run", action="store_true")
    q.set_defaults(fn=cmd_publish)
    q = s.add_parser("comment"); q.add_argument("manifest"); q.set_defaults(fn=cmd_comment)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
