#!/usr/bin/env python3
"""Fetch the promo card image from a Jira ticket's attachments (read-only).

Usage:
  jira-card.py list <ISSUE-KEY>
  jira-card.py download <ISSUE-KEY> <dest_dir>   # newest image attachment

Needs JIRA_EMAIL and JIRA_API_TOKEN in the environment.
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.request

SITE = "https://postmanlabs.atlassian.net"
EMAIL = os.environ.get("JIRA_EMAIL", "")
TOKEN = os.environ.get("JIRA_API_TOKEN", "")
AUTH = "Basic " + base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def get(url, auth=True):
    headers = {"Authorization": AUTH, "Accept": "application/json"} if auth else {}
    req = urllib.request.Request(url, headers=headers)
    opener = urllib.request.build_opener(NoRedirect)
    try:
        return opener.open(req, timeout=30).read()
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308):
            # The media host rejects the Jira Authorization header, so follow the signed URL without it.
            return urllib.request.urlopen(e.headers["Location"], timeout=60).read()
        print(f"ERROR {e.code} from {url}: {e.read().decode()[:300]}", file=sys.stderr)
        sys.exit(1)


def attachments(key):
    data = json.loads(get(f"{SITE}/rest/api/3/issue/{key}?fields=attachment"))
    return data["fields"].get("attachment", [])


def main():
    if not EMAIL or not TOKEN:
        print("ERROR: JIRA_EMAIL and JIRA_API_TOKEN must be set.", file=sys.stderr)
        sys.exit(1)
    args = sys.argv[1:]
    if len(args) < 2 or args[0] not in ("list", "download"):
        print(__doc__)
        sys.exit(1)
    files = attachments(args[1])
    if args[0] == "list":
        for a in files:
            print(f"{a['created']}  {a['mimeType']:<12} {a['filename']}  ({a['size']} bytes)")
        if not files:
            print("No attachments.")
        return
    images = sorted((a for a in files if a["mimeType"].startswith("image/")), key=lambda a: a["created"])
    if not images:
        print("No image attachments on this ticket yet.", file=sys.stderr)
        sys.exit(2)
    pick = images[-1]
    os.makedirs(args[2], exist_ok=True)
    dest = os.path.join(args[2], pick["filename"])
    with open(dest, "wb") as f:
        f.write(get(pick["content"]))
    print(dest)


if __name__ == "__main__":
    main()
