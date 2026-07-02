#!/usr/bin/env python3
import os, sys, json, urllib.request, urllib.parse

API_KEY = os.environ.get("LUMA_API_KEY", "")
BASE_URL = "https://api.lu.ma/public/v1"
CALENDAR_API_ID = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("LUMA_CALENDAR_ID", "cal-TGqTNpY4iyl7XYe")
HEADERS = {
    "x-luma-api-key": API_KEY,
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}

def luma_get(path, params=None):
    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

events, cursor = [], None
while True:
    params = {"calendar_api_id": CALENDAR_API_ID, "pagination_limit": 100}
    if cursor:
        params["pagination_cursor"] = cursor
    data = luma_get("/calendar/list-events", params)
    for e in data.get("entries", []):
        events.append({"name": e.get("name",""), "url": e.get("url",""), "api_id": e.get("api_id",""), "start_at": e.get("start_at","")})
    if not data.get("has_more"):
        break
    cursor = data.get("next_cursor")
    if not cursor:
        break

print(json.dumps(events))
