#!/usr/bin/env python3
"""Parse meetup calendar data from Google Sheets API v4 includeGridData response."""

import sys
import json
import re
from datetime import datetime, date

def parse_date(raw):
    if not raw or not raw.strip():
        return None
    raw = raw.strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%B %d, %Y",
                "%b %d, %Y", "%d %B %Y", "%d %b %Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass
    return None

def find_col(headers, *candidates):
    h_lower = [h.lower() for h in headers]
    for c in candidates:
        for i, h in enumerate(h_lower):
            if c.lower() in h:
                return i
    return None

def cell_value(cell_obj):
    """Extract string value from a gridData cell object."""
    uev = cell_obj.get("userEnteredValue", {})
    return str(uev.get("stringValue", uev.get("numberValue", uev.get("boolValue", "")))).strip()

def is_strikethrough(row_data):
    """Return True if ANY cell in the row has strikethrough formatting."""
    for cell_obj in row_data.get("values", []):
        fmt = cell_obj.get("userEnteredFormat", {})
        if fmt.get("textFormat", {}).get("strikethrough", False):
            return True
    return False

def main():
    data = json.load(sys.stdin)

    try:
        row_data_list = data["sheets"][0]["data"][0]["rowData"]
    except (KeyError, IndexError):
        print(json.dumps({"error": "Unexpected response structure"}))
        return

    if not row_data_list:
        print(json.dumps({"error": "No data returned from sheet"}))
        return

    headers = [cell_value(c) for c in row_data_list[0].get("values", [])]
    raw_rows = row_data_list[1:]

    col = {
        "name":     find_col(headers, "event name", "event", "name", "title"),
        "date":     find_col(headers, "date", "event date", "start"),
        "city":     find_col(headers, "city", "location", "venue city"),
        "country":  find_col(headers, "country", "region"),
        "type":     find_col(headers, "type", "format", "kind"),
        "organizer":find_col(headers, "organizer", "owner", "contact", "host"),
        "status":   find_col(headers, "status", "stage", "state"),
        "url":      find_col(headers, "url", "link", "meetup", "eventbrite"),
        "notes":    find_col(headers, "notes", "comment", "description"),
    }

    def cell(row_values, key):
        idx = col.get(key)
        if idx is None or idx >= len(row_values):
            return ""
        return cell_value(row_values[idx])

    today = date.today()
    upcoming, past, unparsed = [], [], []
    skipped_strikethrough = 0

    for row_obj in raw_rows:
        if is_strikethrough(row_obj):
            skipped_strikethrough += 1
            continue

        row_values = row_obj.get("values", [])
        if not any(cell_value(c) for c in row_values):
            continue

        name = cell(row_values, "name")
        if not name:
            continue

        event_type = cell(row_values, "type")
        if event_type.lower() != "meetup":
            continue

        raw_date = cell(row_values, "date")
        event_date = parse_date(raw_date)

        event = {
            "name": name,
            "date": event_date.isoformat() if event_date else raw_date,
            "date_obj": event_date,
            "city": cell(row_values, "city"),
            "country": cell(row_values, "country"),
            "type": cell(row_values, "type"),
            "organizer": cell(row_values, "organizer"),
            "status": cell(row_values, "status"),
            "url": cell(row_values, "url"),
            "notes": cell(row_values, "notes"),
        }

        if event_date is None:
            unparsed.append(event)
        elif event_date >= today:
            upcoming.append(event)
        else:
            past.append(event)

    upcoming.sort(key=lambda e: e["date_obj"])
    past.sort(key=lambda e: e["date_obj"], reverse=True)

    def region(e):
        parts = [e["city"], e["country"]]
        return ", ".join(p for p in parts if p) or "Unknown"

    region_counts = {}
    for e in upcoming + past:
        r = region(e)
        region_counts[r] = region_counts.get(r, 0) + 1

    for e in upcoming + past + unparsed:
        e.pop("date_obj", None)

    result = {
        "total": len(upcoming) + len(past) + len(unparsed),
        "upcoming": upcoming,
        "past_this_year": [e for e in past if e["date"][:4] == str(today.year)],
        "past_prior_years": [e for e in past if e["date"][:4] != str(today.year)],
        "unparsed_date": unparsed,
        "skipped_strikethrough": skipped_strikethrough,
        "region_summary": sorted(region_counts.items(), key=lambda x: -x[1]),
        "headers_detected": headers,
        "col_map": {k: (headers[v] if v is not None else None) for k, v in col.items()},
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
