#!/usr/bin/env python3
"""Liftoff learning platform totals for qbr-metrics, from the Liftoff admin stats API.

Usage: pull-liftoff.py START END   (YYYY-MM-DD). Prints JSON to stdout.

POST https://www.postman.com/liftoff/api/admin/stats/ (trailing slash required: without it the server answers 308 and a
POST is not retried) with a bearer token in LIFTOFF_ADMIN_API_TOKEN. The request carries the period and a `compare` period;
the API returns metrics, top modules, per-module drop-offs, deltas and a series (weekly for long periods) for both.
The API's `to` date is exclusive, so the pull sends END + 1 day.

Metrics, as the API names them: totalUsers (active in the period), newUsers (signups), stepsCompleted, pointsEarned,
modulesCompleted (one badge per module), anonConversions and anonVisitorConversions. It has no campaign or UTM breakdown.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import timedelta

sys.path.insert(0, os.path.dirname(__file__))
import qbrlib as q  # noqa: E402

URL = os.environ.get("LIFTOFF_ADMIN_URL", "https://www.postman.com/liftoff/api/admin/stats/")
KEYS = ("totalUsers", "newUsers", "stepsCompleted", "pointsEarned", "modulesCompleted", "anonConversions", "anonVisitorConversions")


def main():
    q.load_settings_env()
    token = os.environ.get("LIFTOFF_ADMIN_API_TOKEN")
    if not token:
        sys.exit("LIFTOFF_ADMIN_API_TOKEN is required")
    cur, prev = q.periods(sys.argv[1], sys.argv[2])
    body = {"from": str(cur[0]), "to": str(cur[1] + timedelta(days=1)), "compare": {"from": str(prev[0]), "to": str(prev[1] + timedelta(days=1))}}
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Liftoff admin stats returned HTTP {e.code}: {e.read().decode(errors='replace')[:200]}")
    c, p = d["current"], d["previous"]
    json.dump({
        "granularity": d.get("granularity"),
        "current": {"start": str(cur[0]), "end": str(cur[1]), **{k: c["metrics"].get(k) for k in KEYS}, "top_modules": c["topModules"],
                    "drop_offs": c["dropOffs"], "series": d["series"]},
        "previous": {"start": str(prev[0]), "end": str(prev[1]), **{k: p["metrics"].get(k) for k in KEYS}, "top_modules": p["topModules"],
                     "drop_offs": p["dropOffs"], "series": d["previousSeries"]},
        "change": {k: q.pct_change(c["metrics"].get(k), p["metrics"].get(k)) for k in KEYS},
        "note": "Liftoff admin stats API. modulesCompleted is one badge per module. No campaign or UTM breakdown is available.",
    }, sys.stdout)


if __name__ == "__main__":
    main()
