#!/usr/bin/env python3
"""Fetch Postman Dev Events stats from the Luma Public API."""

import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = os.environ.get("LUMA_API_KEY", "")
BASE_URL = "https://api.lu.ma/public/v1"
CALENDAR_API_ID = "cal-TGqTNpY4iyl7XYe"

# Cloudflare blocks the default Python UA; mimic a browser
HEADERS = {
    "x-luma-api-key": API_KEY,
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}


def luma_get(path, params=None):
    url = f"{BASE_URL}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"ERROR {e.code} from {url}: {body[:400]}", file=sys.stderr)
        sys.exit(1)


def parse_filter(arg):
    if not arg:
        return ("all", None)
    arg = arg.strip()
    for fmt in ("%b-%y", "%b-%Y"):
        try:
            dt = datetime.strptime(arg, fmt)
            return ("month", (dt.month, dt.year))
        except ValueError:
            pass
    try:
        year = int(arg)
        if 2000 <= year <= 2100:
            return ("year", year)
    except ValueError:
        pass
    print(
        f"ERROR: Unrecognised filter '{arg}'. "
        "Use MMM-YY (e.g. Apr-26), YYYY (e.g. 2026), or leave blank.",
        file=sys.stderr,
    )
    sys.exit(1)


def event_in_range(start_at, mode, value):
    if mode == "all":
        return True
    try:
        dt = datetime.fromisoformat(start_at.replace("Z", "+00:00"))
    except Exception:
        return False
    if mode == "month":
        month, year = value
        return dt.month == month and dt.year == year
    if mode == "year":
        return dt.year == value
    return False


def list_all_events():
    """Page through all events for the calendar."""
    events = []
    cursor = None
    while True:
        params = {"calendar_api_id": CALENDAR_API_ID, "pagination_limit": 100}
        if cursor:
            params["pagination_cursor"] = cursor
        data = luma_get("/calendar/list-events", params)
        for entry in data.get("entries", []):
            events.append(entry)
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
        if not cursor:
            break
    return events


def count_guests(event_api_id):
    """Page through all guests for an event and return (registered, waitlisted, checked_in)."""
    registered = waitlisted = checked_in = 0
    cursor = None
    while True:
        params = {"event_api_id": event_api_id, "pagination_limit": 500}
        if cursor:
            params["pagination_cursor"] = cursor
        data = luma_get("/event/get-guests", params)
        for g in data.get("entries", []):
            status = g.get("approval_status", "")
            if status == "approved":
                registered += 1
            elif status in ("waitlisted", "pending"):
                waitlisted += 1
            if g.get("checked_in_at"):
                checked_in += 1
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
        if not cursor:
            break
    return registered, waitlisted, checked_in


def score_out_of_5(registered, checked_in):
    """Return attendance as x.x out of 5.0. Returns None if no registrations."""
    if not registered:
        return None
    return round((checked_in / registered) * 5.0, 1)


def main():
    if not API_KEY:
        print("ERROR: LUMA_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    filter_arg = sys.argv[1] if len(sys.argv) > 1 else ""
    mode, value = parse_filter(filter_arg)

    print("Fetching event list...", file=sys.stderr)
    all_events = list_all_events()

    filtered = [
        ev for ev in all_events
        if event_in_range(ev.get("start_at", ""), mode, value)
    ]
    filtered.sort(key=lambda e: e.get("start_at", ""), reverse=True)

    print(f"Found {len(filtered)} event(s) matching filter '{filter_arg or 'all time'}' — fetching guest counts in parallel...", file=sys.stderr)

    def fetch_row(ev):
        api_id = ev.get("api_id", ev.get("id", ""))
        registered, waitlisted, checked_in = count_guests(api_id)
        start_raw = ev.get("start_at", "")
        try:
            dt = datetime.fromisoformat(start_raw.replace("Z", "+00:00"))
            date_str = dt.strftime("%d %b %Y")
        except Exception:
            date_str = start_raw[:10] if start_raw else "Unknown"
        return {
            "name": ev.get("name", "Untitled"),
            "date": date_str,
            "registered": registered,
            "waitlisted": waitlisted,
            "checked_in": checked_in,
            "score": score_out_of_5(registered, checked_in),
            "url": ev.get("url", ""),
            "_start_at": ev.get("start_at", ""),
        }

    with ThreadPoolExecutor(max_workers=min(8, len(filtered) or 1)) as pool:
        futures = {pool.submit(fetch_row, ev): ev.get("name", "") for ev in filtered}
        raw_rows = []
        for future in as_completed(futures):
            raw_rows.append(future.result())
            print(f"  done: {futures[future][:60]}", file=sys.stderr)

    rows = sorted(raw_rows, key=lambda r: r.pop("_start_at"), reverse=True)

    total_registered = sum(r["registered"] for r in rows)
    total_waitlisted = sum(r["waitlisted"] for r in rows)
    total_checked_in = sum(r["checked_in"] for r in rows)
    overall_score = score_out_of_5(total_registered, total_checked_in)

    result = {
        "calendar_name": "Postman Developer Events",
        "filter": filter_arg or "all time",
        "event_count": len(rows),
        "events": rows,
        "totals": {
            "registered": total_registered,
            "waitlisted": total_waitlisted,
            "checked_in": total_checked_in,
            "score": overall_score,
        },
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
