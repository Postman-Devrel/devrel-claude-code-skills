#!/usr/bin/env python3
"""Shared WordPress auth setup and utilities for the blog scheduler skill."""
import os, json, base64, urllib.request, urllib.parse
from datetime import datetime, timedelta, timezone

WP_BASE = "https://blog.postman.com/wp-json/wp/v2"
username = os.environ["WP_USERNAME"]
app_password = os.environ["WP_APP_PASSWORD"]
auth = base64.b64encode(f"{username}:{app_password}".encode()).decode()
headers = {
    "Authorization": f"Basic {auth}",
    "User-Agent": "PostmanDevRelDashboard/1.0",
}

PST = timezone(timedelta(hours=-8))

def wp_get(path):
    req = urllib.request.Request(f"{WP_BASE}/{path}", headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def us_public_holidays(year):
    """Return a set of date strings (YYYY-MM-DD) for US public holidays in the given year."""
    from datetime import date
    holidays = set()

    for month, day in [(1, 1), (6, 19), (7, 4), (11, 11), (12, 25)]:
        holidays.add(date(year, month, day).isoformat())

    def nth_weekday(y, m, weekday, n):
        first = date(y, m, 1)
        offset = (weekday - first.weekday()) % 7
        return date(y, m, 1 + offset + 7 * (n - 1))

    def last_weekday(y, m, weekday):
        last_day = date(y + 1, 1, 1) - timedelta(days=1) if m == 12 else date(y, m + 1, 1) - timedelta(days=1)
        offset = (last_day.weekday() - weekday) % 7
        return last_day - timedelta(days=offset)

    holidays.add(nth_weekday(year, 1, 0, 3).isoformat())   # MLK Day
    holidays.add(nth_weekday(year, 2, 0, 3).isoformat())   # Presidents' Day
    holidays.add(last_weekday(year, 5, 0).isoformat())      # Memorial Day
    holidays.add(nth_weekday(year, 9, 0, 1).isoformat())   # Labor Day
    holidays.add(nth_weekday(year, 10, 0, 2).isoformat())  # Columbus Day
    holidays.add(nth_weekday(year, 11, 3, 4).isoformat())  # Thanksgiving

    return holidays
