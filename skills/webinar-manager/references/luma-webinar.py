#!/usr/bin/env python3
"""Luma helper for webinar-manager: get, diff/update, create, and guest stats.

Usage:
  luma-webinar.py get <event_api_id>
  luma-webinar.py update <event_api_id> <payload.json> [--apply]   # diff only unless --apply
  luma-webinar.py create <payload.json> [--apply]                  # prints payload only unless --apply
  luma-webinar.py add-host <event_api_id> <email> <name> [--apply]  # prints body only unless --apply
  luma-webinar.py stats <event_api_id>
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API_KEY = os.environ.get("LUMA_API_KEY", "")
BASE_URL = "https://api.lu.ma/public/v1"

# Cloudflare blocks the default Python UA; mimic a browser
HEADERS = {
    "x-luma-api-key": API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}


def call(method, path, params=None, body=None):
    url = f"{BASE_URL}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        print(f"ERROR {e.code} from {url}: {e.read().decode()[:600]}", file=sys.stderr)
        sys.exit(1)


def get_event(api_id):
    data = call("GET", "/event/get", {"api_id": api_id})
    return data.get("event", data)


def load_payload(path):
    with open(path) as f:
        return json.load(f)


def diff(current, payload):
    rows = []
    for key, new in payload.items():
        old = current.get(key)
        if old != new:
            rows.append((key, old, new))
    return rows


def cmd_get(api_id):
    print(json.dumps(get_event(api_id), indent=2))


def cmd_update(api_id, payload_path, apply):
    payload = load_payload(payload_path)
    current = get_event(api_id)
    rows = diff(current, payload)
    if not rows:
        print("No changes: the event already matches the payload.")
        return
    print(f"{len(rows)} field(s) would change on {api_id}:")
    for key, old, new in rows:
        print(f"\n- {key}\n    current: {json.dumps(old)[:300]}\n    new:     {json.dumps(new)[:300]}")
    if not apply:
        print("\nDry run. Re-run with --apply to write these changes.")
        return
    resp = call("POST", "/event/update", body={"api_id": api_id, **{k: n for k, _, n in rows}})
    print("\nUpdate response:")
    print(json.dumps(resp, indent=2))


def cmd_create(payload_path, apply):
    payload = load_payload(payload_path)
    if not apply:
        print("Dry run. Would create event with payload:")
        print(json.dumps(payload, indent=2))
        print("\nRe-run with --apply to create it.")
        return
    resp = call("POST", "/event/create", body=payload)
    print(json.dumps(resp, indent=2))


def cmd_add_host(api_id, email, name, apply):
    body = {"event_api_id": api_id, "email": email, "name": name}
    if not apply:
        print("Dry run. Would add host:")
        print(json.dumps(body, indent=2))
        print("\nRe-run with --apply to add the host.")
        return
    print(json.dumps(call("POST", "/event/add-host", body=body), indent=2))


def cmd_stats(api_id):
    registered = waitlisted = checked_in = 0
    cursor = None
    while True:
        params = {"event_api_id": api_id, "pagination_limit": 500}
        if cursor:
            params["pagination_cursor"] = cursor
        data = call("GET", "/event/get-guests", params)
        for g in data.get("entries", []):
            status = g.get("approval_status", "")
            if status == "approved":
                registered += 1
            elif status in ("waitlisted", "pending"):
                waitlisted += 1
            if g.get("checked_in_at"):
                checked_in += 1
        cursor = data.get("next_cursor")
        if not data.get("has_more") or not cursor:
            break
    rate = round(checked_in / registered * 100, 1) if registered else None
    print(json.dumps({
        "event_api_id": api_id,
        "registered": registered,
        "waitlisted": waitlisted,
        "checked_in": checked_in,
        "attendance_rate_pct": rate,
    }, indent=2))


def main():
    if not API_KEY:
        print("ERROR: LUMA_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)
    args = [a for a in sys.argv[1:] if a != "--apply"]
    apply = "--apply" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(1)
    cmd = args[0]
    try:
        if cmd == "get":
            cmd_get(args[1])
        elif cmd == "update":
            cmd_update(args[1], args[2], apply)
        elif cmd == "create":
            cmd_create(args[1], apply)
        elif cmd == "add-host":
            cmd_add_host(args[1], args[2], args[3], apply)
        elif cmd == "stats":
            cmd_stats(args[1])
        else:
            print(__doc__)
            sys.exit(1)
    except IndexError:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
