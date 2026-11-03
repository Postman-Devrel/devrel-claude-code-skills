#!/usr/bin/env python3
"""Luma metrics for qbr-metrics: events, registrations, attendance, geography, contacts.

Usage: pull-luma.py START END   (YYYY-MM-DD). Prints JSON to stdout.

Feedback ratings and attendee geography are not exposed by the Luma API, so
they are reported as unavailable. Geography is by event location only.
"""
import collections
import json
import os
import sys
import time
from datetime import timedelta

sys.path.insert(0, os.path.dirname(__file__))
import qbrlib as q  # noqa: E402

BASE = "https://public-api.luma.com"


def hdr():
    key = os.environ.get("LUMA_API_KEY")
    if not key:
        sys.exit("LUMA_API_KEY is required")
    return {"x-luma-api-key": key, "accept": "application/json"}


def paged(path, h, **params):
    cursor = None
    while True:
        p = dict(params)
        if cursor:
            p["pagination_cursor"] = cursor
        status, body = q.http_json(f"{BASE}{path}?{q.urllib.parse.urlencode(p)}", h)
        if status != 200:
            sys.exit(f"Luma {path} failed: HTTP {status} {str(body)[:200]}")
        yield from body.get("entries", [])
        if not body.get("has_more"):
            return
        cursor = body.get("next_cursor")
        time.sleep(0.25)  # stay under Luma's rate limit


def guest_counts(h, event_id):
    reg = wait = attended = 0
    for g in paged("/v1/events/guests/list", h, event_id=event_id, pagination_limit=50):
        status = g.get("approval_status")
        if status == "approved":
            reg += 1
        elif status == "waitlist":
            wait += 1
        if any(t.get("checked_in_at") for t in (g.get("event_tickets") or [])):
            attended += 1
    return reg, wait, attended


def events_window(h, start, end):
    after = f"{start}T00:00:00.000Z"
    before = f"{end + timedelta(days=1)}T00:00:00.000Z"
    events = []
    for e in paged("/v1/calendars/events/list", h, after=after, before=before, pagination_limit=50):
        ev = e.get("event", e)
        geo = ev.get("geo_address_json") or {}
        reg, wait, att = guest_counts(h, ev["id"])
        q.log(f"  {ev['start_at'][:10]} {ev['name'][:50]}: registered={reg} attended={att}")
        events.append({
            "name": ev["name"], "date": ev["start_at"][:10], "url": ev.get("url"),
            "location_type": ev.get("location_type"),
            "city": geo.get("city"), "region": geo.get("region"), "country": geo.get("country"),
            "registered": reg, "waitlisted": wait, "attended": att,
        })
    events.sort(key=lambda e: e["date"])
    unset = lambda e: "Online" if e["location_type"] == "online" else "Location not set in Luma"  # noqa: E731
    by_city = collections.Counter((f"{e['city']}, {e['country']}" if e["city"] else unset(e)) for e in events)
    by_country = collections.Counter((e["country"] or unset(e)) for e in events)
    reg = sum(e["registered"] for e in events)
    att = sum(e["attended"] for e in events)
    return {
        "start": str(start), "end": str(end),
        "events": len(events), "registered": reg,
        "waitlisted": sum(e["waitlisted"] for e in events), "attended": att,
        "attendance_rate_pct": round(att / reg * 100, 1) if reg else None,
        "by_city": dict(by_city.most_common()), "by_country": dict(by_country.most_common()),
        "event_list": events,
    }


FREE_MAIL = {"gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.in", "yahoo.co.uk", "hotmail.com", "outlook.com",
             "live.com", "msn.com", "icloud.com", "me.com", "aol.com", "proton.me", "protonmail.com", "qq.com", "163.com",
             "126.com", "yandex.com", "yandex.ru", "mail.com", "gmx.com", "gmx.de", "web.de", "rediffmail.com", "zoho.com"}


def contacts_growth(h, windows):
    """Count calendar contacts by created_at, plus corporate email domains first seen per window.

    A "new account" here is a corporate (non free-mail) email domain whose earliest calendar contact
    was created in the window. It is a proxy for accounts reached through Luma; it does not include
    events outside Luma and cannot see contacts who register with a personal address.
    """
    total = 0
    daily = collections.Counter()
    first_seen = {}  # domain -> earliest created date
    q.log("  paging calendar contacts ...")
    for c in paged("/v1/calendars/contacts/list", h, pagination_limit=50):
        total += 1
        created = (c.get("created_at") or "")[:10]
        daily[created] += 1
        domain = (c.get("email") or "").rsplit("@", 1)[-1].lower().strip()
        if created and domain and "." in domain and domain not in FREE_MAIL:
            if domain not in first_seen or created < first_seen[domain]:
                first_seen[domain] = created
    out = {"total_now": total, "corporate_domains_total": len(first_seen)}
    for name, (start, end) in windows.items():
        new = sum(v for k, v in daily.items() if k and start <= q.d(k) <= end)
        before_end = sum(v for k, v in daily.items() if k and q.d(k) <= end)
        new_domains = sum(1 for dte in first_seen.values() if start <= q.d(dte) <= end)
        out[name] = {
            "new": new, "total_at_end": before_end,
            "new_corporate_domains": new_domains,
            "corporate_domains_at_end": sum(1 for dte in first_seen.values() if q.d(dte) <= end),
            "weekly_new": q.weekly(daily, start, end),
        }
    return out


def main():
    q.load_settings_env()
    cur, prev = q.periods(sys.argv[1], sys.argv[2])
    h = hdr()
    q.log("Luma: current period events")
    c = events_window(h, *cur)
    q.log("Luma: previous period events")
    p = events_window(h, *prev)
    contacts = contacts_growth(h, {"current": cur, "previous": prev})
    result = {
        "current": c, "previous": p, "contacts": contacts,
        "change": {k: q.pct_change(c[k], p[k]) for k in ("events", "registered", "attended")},
        "contacts_change_new": q.pct_change(contacts["current"]["new"], contacts["previous"]["new"]),
        "new_domains_change": q.pct_change(contacts["current"]["new_corporate_domains"], contacts["previous"]["new_corporate_domains"]),
        "feedback_ratings": "not available (the Luma API has no feedback or rating data)",
        "attendee_geography": "not available (guest records have no location)",
    }
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
