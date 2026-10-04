"""YouTube side of the publisher (YouTube Data API v3). One OAuth client for everything, one token per channel:
  ~/.config/channel-forge/client_secret.json      Desktop-type OAuth client from Google Cloud (see README)
  ~/.config/channel-forge/youtube/<slug>.json     token, created by `publish.py auth <slug>`"""
import os, sys, time

CFG = os.path.expanduser("~/.config/channel-forge")
CLIENT = os.path.join(CFG, "client_secret.json")
SLUG = None  # set by publish.py before any call
TOKEN = lambda: os.path.join(CFG, "youtube", f"{SLUG}.json")
# `youtube` is needed to change the schedule of an already-uploaded video (videos.update).
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube",
          "https://www.googleapis.com/auth/youtube.readonly"]


def creds():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    if not os.path.exists(TOKEN()):
        sys.exit("no YouTube token: run `publish.py auth <slug>` first")
    c = Credentials.from_authorized_user_file(TOKEN())
    if not set(SCOPES) <= set(c.scopes or []):
        sys.exit("YouTube token is missing permissions: run `publish.py auth <slug>` again")
    if not c.valid:
        if c.expired and c.refresh_token:
            c.refresh(Request())
            open(TOKEN(), "w").write(c.to_json())
        else:
            sys.exit("YouTube token invalid: run `publish.py auth <slug>` again")
    return c


def client():
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=creds(), cache_discovery=False)


def auth():
    from google_auth_oauthlib.flow import InstalledAppFlow
    if not os.path.exists(CLIENT):
        sys.exit(f"missing OAuth client: put a Desktop-type client_secret.json at {CLIENT}")
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT, SCOPES)
    # Fixed port so a stale tab never points at a dead listener; the listener waits until consent completes.
    c = flow.run_local_server(port=8765, prompt="consent", access_type="offline", open_browser=True, timeout_seconds=3600,
                              authorization_prompt_message="Open this URL, sign in, and CHOOSE THE YOUTUBE CHANNEL for " + SLUG + ":\n{url}\n")
    os.makedirs(os.path.dirname(TOKEN()), exist_ok=True)
    open(TOKEN(), "w").write(c.to_json())
    os.chmod(TOKEN(), 0o600)
    return channel(client())


def channel(y):
    items = y.channels().list(part="snippet", mine=True).execute().get("items", [])
    return (items[0]["id"], items[0]["snippet"]["title"]) if items else (None, None)


def upload(y, item, path, publish_at):
    from googleapiclient.http import MediaFileUpload
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "embeddable": True}
    if publish_at:
        status["publishAt"] = publish_at  # private until then; YouTube publishes it automatically
    body = {"snippet": {"title": item["title"], "description": item["description"], "tags": item.get("tags", []),
                        "categoryId": str(item.get("categoryId", 24)), "defaultLanguage": item.get("lang", "en"), "defaultAudioLanguage": item.get("lang", "en")},
            "status": status}
    media = MediaFileUpload(path, chunksize=16 * 1024 * 1024, resumable=True, mimetype="video/mp4")
    req = y.videos().insert(part="snippet,status", body=body, media_body=media, notifySubscribers=True)
    resp, tries = None, 0
    while resp is None:
        try:
            _, resp = req.next_chunk()
        except Exception as e:  # transient network / 5xx: back off and resume the same session
            tries += 1
            if tries > 6:
                raise
            print(f"  retry {tries}: {str(e)[:120]}")
            time.sleep(min(60, 2 ** tries))
    return resp["id"]


def reschedule(y, vid, publish_at):
    y.videos().update(part="status", body={"id": vid, "status": {"privacyStatus": "private", "publishAt": publish_at,
                                                                 "selfDeclaredMadeForKids": False, "embeddable": True}}).execute()


def set_thumb(y, vid, path):
    from googleapiclient.http import MediaFileUpload
    try:
        y.thumbnails().set(videoId=vid, media_body=MediaFileUpload(path)).execute()
        return "ok"
    except Exception as e:  # e.g. 403 until the channel is phone-verified; the video itself is already up
        return f"failed: {str(e)[:200]}"


def comment(y, vid, text):
    """Top-level comment from the channel (photo credits). Pinning is not available in the API: pin it in Studio."""
    y.commentThreads().insert(part="snippet", body={"snippet": {"videoId": vid, "topLevelComment": {"snippet": {"textOriginal": text}}}}).execute()


def brand(y, banner=None, description=None, keywords=None, country=None):
    """Banner (2560x1440, safe area 1546x423 centred, <6 MB) + channel description/keywords. Name and avatar are manual."""
    from googleapiclient.http import MediaFileUpload
    ch = y.channels().list(part="brandingSettings", mine=True).execute()["items"][0]
    bs = ch.get("brandingSettings", {})
    bs.setdefault("channel", {})
    if description is not None:
        bs["channel"]["description"] = description[:1000]
    if keywords is not None:
        bs["channel"]["keywords"] = " ".join(f'"{k}"' if " " in k else k for k in keywords)[:500]
    if country:
        bs["channel"]["country"] = country
    if banner:
        url = y.channelBanners().insert(media_body=MediaFileUpload(banner, mimetype="image/jpeg" if banner.lower().endswith(("jpg", "jpeg")) else "image/png")).execute()["url"]
        bs.setdefault("image", {})["bannerExternalUrl"] = url
    bs["channel"].pop("title", None)  # the API ignores/forbids title edits; the name is changed in YouTube Studio
    y.channels().update(part="brandingSettings", body={"id": ch["id"], "brandingSettings": bs}).execute()
    return ch["id"]
