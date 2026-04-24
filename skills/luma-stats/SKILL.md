---
name: luma-stats
description: "Pull event statistics from the Postman Dev Events Luma calendar — registrations, waitlist, attendee count, and engagement score per event. Supports filtering by MMM-YY (e.g. Apr-26), YYYY (e.g. 2026), or blank for all time. Shows sum totals across all matching events."
argument-hint: "[MMM-YY | YYYY] (optional, e.g. 'Apr-26' or '2026' — blank for all time)"
---

# Luma Event Stats

Pull registration, waitlist, attendance, and engagement data for all events on the [Postman Dev Events](https://luma.com/postman-dev-events) Luma calendar. Useful for measuring event program health, spotting trends, and reporting on community growth.

## How the data is fetched

The Luma Public API v1 does not include guest counts directly on event objects. Stats are derived by paging through dedicated endpoints:

- **Registered** — guests with `approval_status == "approved"` (from `event/get-guests`)
- **Waitlisted** — guests with `approval_status == "waitlisted"` or `"pending"` (from `event/get-guests`)
- **Attended** — guests where `checked_in_at` is not null (from `event/get-guests`)
- **Score** — `(attended ÷ registered) × 5.0`, shown as `x.x/5.0`
Progress is printed to stderr as each event is processed.

---

## Configuration

This skill requires a Luma API key with read access to the calendar.

### Setup

1. **Get your Luma API key:**
   - Log in to [lu.ma](https://lu.ma) as a calendar admin
   - Go to **Settings → Integrations → API**
   - Create a new API key with read permissions

2. **Set the environment variable** in `.claude/settings.json`:
   ```json
   {
     "env": {
       "LUMA_API_KEY": "your-luma-api-key"
     }
   }
   ```

---

## Process

### Step 1: Verify API key

Check that `LUMA_API_KEY` is set. If it is not present, stop and tell the user to set the environment variable as described above.

```bash
echo $LUMA_API_KEY
```

### Step 2: Write and run the data-fetch script

Write the following Python script to `/tmp/luma-stats.py`, then execute it.

```python
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
            # Entry IS the event object (api_id, name, start_at, url, ...)
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
```

Run the script with the filter argument (if provided):

```bash
# With month filter
python3 /tmp/luma-stats.py "Apr-26"

# With year filter
python3 /tmp/luma-stats.py "2026"

# All time
python3 /tmp/luma-stats.py
```

Capture the JSON from stdout. Progress messages go to stderr and can be ignored.

---

### Step 3: Render the report

From the JSON output, produce a clean markdown report and display it in the chat immediately.

```
## Luma Event Stats — Postman Developer Events
**Filter:** {filter}  |  **Events:** {N}

| Date | Event | Registered | Waitlisted | Attended | Score |
|------|-------|-----------|-----------|---------|-------|
| 15 Apr 2026 | NYC Meetup | 142 | 23 | 98 | 3.4/5.0 |
| 03 Apr 2026 | London Meetup | 87 | 0 | 71 | 4.1/5.0 |
| **TOTAL** | **{N} events** | **{sum}** | **{sum}** | **{sum}** | **{score}/5.0** |

**Score** = (checked-in ÷ registered) × 5.0. Future events show `—` until check-in data is recorded.
```

- Sort events newest-first
- Append `%` to score values
- Show `—` for score when registered = 0
- Bold the TOTAL row

### Step 4: Save to file

Save the same report to `luma-output/` — create the directory if it doesn't exist.

Filename pattern:
- All time → `luma-output/luma-stats-all-time.md`
- Year → `luma-output/luma-stats-2026.md`
- Month → `luma-output/luma-stats-Apr-26.md`

Append a **Notes** section at the bottom of the file:
```markdown
---
*Generated: {today's date} | Calendar: https://luma.com/postman-dev-events*
*Score = checked-in ÷ registered × 100. Future events show 0 attended until check-in data is recorded.*
*Subscriber count not available via Luma Public API v1.*
```

---

## Score Metric

Score = `(checked-in ÷ registered) × 5.0`, displayed as `x.x/5.0`.

| Score | Interpretation |
|-------|---------------|
| 4.0–5.0 | Excellent turnout |
| 3.0–3.9 | Good — typical for in-person tech meetups |
| 2.0–2.9 | Below average — consider venue, timing, or topic |
| < 2.0 | Low — flag for review |
| — | No registrations, or future event with no check-in data yet |

---

## Error Handling

| Error | Action |
|-------|--------|
| `LUMA_API_KEY` not set | Stop. Show setup instructions above. |
| HTTP 403 Cloudflare block | The User-Agent header is required — verify it is present in `HEADERS`. |
| HTTP 401 Unauthorized | API key is invalid or expired. Ask user to regenerate in Luma Settings → Integrations → API. |
| Zero events returned | Check that the filter format is correct (e.g. `Apr-26` not `April-26`). Print the parsed filter value. |
| All counts are 0 | Future events have no check-ins yet — this is expected. Past events with 0 attended may not have used Luma check-in. |
