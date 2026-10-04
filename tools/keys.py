#!/usr/bin/env python3
"""Store API keys locally (hidden input, file mode 600). Run in your own terminal so keys never pass through the chat.

  keys.py set <name>      name: elevenlabs_api_key | gemini_api_key | openai_api_key | socialbunny_api_key
  keys.py list            which keys are set (values never printed)
"""
import getpass, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CFG  # noqa: E402

NAMES = ("elevenlabs_api_key", "gemini_api_key", "openai_api_key", "socialbunny_api_key")
P = os.path.join(CFG, "keys.json")


def load():
    return json.load(open(P)) if os.path.exists(P) else {}


def main():
    a = sys.argv[1:]
    if a[:1] == ["list"]:
        k = load()
        for n in NAMES:
            print(f"{n:22s} {'set' if k.get(n) else '-'}")
    elif len(a) == 2 and a[0] == "set" and a[1] in NAMES:
        v = getpass.getpass(f"{a[1]} (input hidden): ").strip()
        if not v:
            sys.exit("nothing entered")
        k = load(); k[a[1]] = v
        os.makedirs(CFG, exist_ok=True)
        fd = os.open(P, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as fh:
            json.dump(k, fh)
        os.chmod(P, 0o600)
        print(f"saved {a[1]} to {P}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
