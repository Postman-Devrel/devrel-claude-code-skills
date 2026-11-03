#!/usr/bin/env python3
"""Meetup sheet metrics for qbr-metrics: ratings, cost, cost per attendee, Luma subscribers.

Usage: pull-sheet.py START END   (YYYY-MM-DD). Prints JSON to stdout.

Reads the "Meetups & User Group Cal" tab of the FY27 Developer Meetups sheet (MEETUP_SHEET_ID)
with the same Google service account as meetup-calendar (GOOGLE_APPLICATION_CREDENTIALS).
Columns: S = Cost, T = Cost per attendee, U = Rating (out of 5). Blank means not recorded and is
never treated as zero. A "$0" cost is kept as zero (co-hosted or sponsored events) and reported
separately, because it would otherwise drag the average cost per attendee down.
"""
import json
import os
import re
import statistics
import subprocess
import sys
import urllib.parse
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
import qbrlib as q  # noqa: E402

TAB = "Meetups & User Group Cal"
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def token():
    script = os.path.join(os.path.dirname(__file__), "..", "..", "meetup-calendar", "references", "get-google-token.py")
    proc = subprocess.run([sys.executable, script], capture_output=True, text=True)
    t = proc.stdout.strip()
    if not t.startswith("ya29"):
        sys.exit("Could not get a Google token (check GOOGLE_APPLICATION_CREDENTIALS): " + proc.stderr[:200])
    return t


def money(s):
    s = (s or "").strip()
    if not s or s in ("-", "#DIV/0!"):
        return None
    try:
        return float(re.sub(r"[$,]", "", s))
    except ValueError:
        return None


def number(s):
    s = (s or "").strip().replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def parse_date(s):
    for fmt in ("%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime((s or "").strip(), fmt).date()
        except ValueError:
            pass
    return None


def cell(r, i):
    return (r[i] if i < len(r) else "").strip().replace("\n", " ")


def parse_events(rows):
    events = []
    for r in rows[28:]:
        name, d = cell(r, 1), parse_date(cell(r, 5))
        if not d or name.upper() == "TOTAL":
            continue
        att, reg = number(cell(r, 16)), number(cell(r, 15))
        events.append({
            "name": name, "type": cell(r, 4), "date": d, "location": cell(r, 9), "region": cell(r, 10),
            "registered": int(reg) if reg is not None else None,
            "attendees": int(att) if att is not None else None,
            "cost": money(cell(r, 18)), "rating": number(cell(r, 20)),
            "hit_capacity": cell(r, 21) or None, "partners": cell(r, 2) or None, "notes": cell(r, 22) or None,
            "luma_url": cell(r, 23) or None,
        })
    return events


def subscribers(rows):
    """Monthly Luma subscriber totals from the 'Postman Events' row under the header row."""
    for i, r in enumerate(rows[:40]):
        if cell(r, 1) == "Luma Subscribers":
            header, data = r, next((x for x in rows[i + 1:i + 4] if cell(x, 1) == "Postman Events"), None)
            out = {}
            for j in range(3, len(header)):
                m = re.fullmatch(r"(\d{4})-([A-Za-z]{3})[a-z]*", cell(header, j))
                v = number(cell(data, j)) if data else None
                if m and v is not None and v > 0:
                    out[f"{m.group(1)}-{MONTHS[m.group(2).lower()[:3]]:02d}"] = int(v)
            return out
    return {}


def window(events, start, end):
    start, end = q.d(start), q.d(end)
    ev = [e for e in events if start <= e["date"] <= end]
    reported = [e for e in ev if e["attendees"] is not None]
    rated = [e for e in ev if e["rating"] is not None]
    costed = [e for e in reported if e["cost"] is not None and e["cost"] > 0]
    zero_cost = [e for e in reported if e["cost"] == 0]
    spend = sum(e["cost"] for e in costed)
    att_costed = sum(e["attendees"] for e in costed)
    by_region = {}
    for e in costed:
        g = by_region.setdefault(e["region"] or "Unknown", {"events": 0, "cost": 0.0, "attendees": 0})
        g["events"] += 1
        g["cost"] += e["cost"]
        g["attendees"] += e["attendees"]
    for g in by_region.values():
        g["cost_per_attendee"] = round(g["cost"] / g["attendees"], 2) if g["attendees"] else None
    cpas = sorted(((e["cost"] / e["attendees"], e) for e in costed if e["attendees"]), key=lambda x: x[0])
    ser = lambda e: {k: (str(v) if k == "date" else v) for k, v in e.items()}  # noqa: E731
    return {
        "start": str(start), "end": str(end),
        "events_in_sheet": len(ev),
        "events_with_attendance": len(reported),
        "events_without_data": len(ev) - len(reported),
        "attendees": sum(e["attendees"] for e in reported),
        "events_rated": len(rated),
        "avg_rating": round(statistics.mean(e["rating"] for e in rated), 2) if rated else None,
        "attendee_weighted_rating": (round(sum(e["rating"] * (e["attendees"] or 0) for e in rated)
                                           / sum((e["attendees"] or 0) for e in rated), 2)
                                     if rated and sum((e["attendees"] or 0) for e in rated) else None),
        "lowest_rated": [ser(e) for e in sorted(rated, key=lambda e: e["rating"])[:3]],
        "total_cost": round(spend, 2),
        "events_with_cost": len(costed),
        "zero_cost_events": len(zero_cost),
        "cost_per_attendee": round(spend / att_costed, 2) if att_costed else None,
        "median_cost_per_attendee": round(statistics.median(c for c, _ in cpas), 2) if cpas else None,
        "cheapest_per_attendee": [dict(ser(e), cost_per_attendee=round(c, 2)) for c, e in cpas[:3]],
        "priciest_per_attendee": [dict(ser(e), cost_per_attendee=round(c, 2)) for c, e in cpas[-3:][::-1]],
        "by_region": by_region,
        "events": [ser(e) for e in ev],
    }


def main():
    q.load_settings_env()
    sid = os.environ.get("MEETUP_SHEET_ID")
    if not sid:
        sys.exit("MEETUP_SHEET_ID is required")
    h = {"Authorization": "Bearer " + token()}
    rng = urllib.parse.quote(f"'{TAB}'!A1:AJ1043")
    status, body = q.http_json(f"https://sheets.googleapis.com/v4/spreadsheets/{sid}/values/{rng}?valueRenderOption=FORMATTED_VALUE", h)
    if status != 200:
        sys.exit(f"Sheets API failed: HTTP {status} {str(body)[:200]}")
    rows = body.get("values", [])
    events = parse_events(rows)
    cur, prev = q.periods(sys.argv[1], sys.argv[2])
    c, p = window(events, *cur), window(events, *prev)
    subs = subscribers(rows)
    json.dump({
        "current": c, "previous": p, "luma_subscribers_by_month": subs,
        "change": {k: q.pct_change(c[k], p[k]) for k in ("total_cost", "cost_per_attendee", "avg_rating", "attendees")},
        "notes": "Blank cells are not recorded and are excluded, not zero. $0 cost is kept as zero and reported separately.",
    }, sys.stdout)


if __name__ == "__main__":
    main()
