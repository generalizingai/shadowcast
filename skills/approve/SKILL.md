---
name: approve
description: Approve or reject an episode script that is waiting for review in a shadowcast channel. Use when the user says approve, looks good, ship it, or gives script feedback for an episode.
argument-hint: <channel slug> <episode ID> [reject: <feedback>]
---

# Approve a script

`T="${CLAUDE_PLUGIN_ROOT}/tools"`

1. Run `python3 "$T/ep.py" list <slug>`. Find the episode; it must be `awaiting_approval`.
   - With no ID given, list every waiting episode and ask which one.
2. If the user hasn't seen the script in this conversation, show its title, its sections and a 5-line summary. The full text is at `<dir>/SCRIPT.md`.
3. **Approve:** run `python3 "$T/ep.py" set <slug> <ID> approved`. Then continue the episode pipeline right away (the episode skill, from "approved"), unless the user only wanted to approve.
4. **Reject or change:** run `python3 "$T/ep.py" set <slug> <ID> researched "feedback=<the user's notes, verbatim>"`. The next run rewrites the script with that feedback.
   - Offer to rewrite it now.
