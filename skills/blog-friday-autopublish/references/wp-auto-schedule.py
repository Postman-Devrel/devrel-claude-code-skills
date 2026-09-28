#!/usr/bin/env python3
"""Auto-schedule a freshly staged draft to the next open Tue/Thu slot (Mon/Wed
fallback, then further out), same priority rules as blog-wordpress-scheduler,
but with no embargo and no human confirmation step."""
import os, json, base64, urllib.request
from datetime import date, timedelta, datetime, timezone

WP_BASE = "https://blog.postman.com/wp-json/wp/v2"
username = os.environ["WP_USERNAME"]
app_password = os.environ["WP_APP_PASSWORD"]
auth = base64.b64encode(f"{username}:{app_password}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "User-Agent": "PostmanDevRelDashboard/1.0"}

PST = timezone(timedelta(hours=-8))


def wp_get(path):
    req = urllib.request.Request(f"{WP_BASE}/{path}", headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def us_public_holidays(year):
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


POST_ID = 0  # Replace with the post ID from Step 5

today_date = datetime.now(PST).date()
holidays = us_public_holidays(today_date.year)
two_weeks_out = today_date + timedelta(weeks=2)
if two_weeks_out.year != today_date.year:
    holidays |= us_public_holidays(two_weeks_out.year)

earliest = today_date + timedelta(days=1)


def slot_available(candidate):
    cand_str = candidate.isoformat()
    if cand_str in holidays:
        return False
    existing = wp_get(f"posts?status=future&after={cand_str}T00:00:00&before={cand_str}T23:59:59&per_page=10")
    return not [p for p in existing if p["id"] != POST_ID]


target = None
candidate = earliest
while candidate <= two_weeks_out:
    if candidate.weekday() in (1, 3) and slot_available(candidate):
        target = candidate
        break
    candidate += timedelta(days=1)

if not target:
    candidate = earliest
    while candidate <= two_weeks_out:
        if candidate.weekday() in (0, 2) and slot_available(candidate):
            target = candidate
            break
        candidate += timedelta(days=1)

if not target:
    priority_days = [1, 3, 2, 0]
    check_from = two_weeks_out + timedelta(days=1)
    week_start = check_from - timedelta(days=check_from.weekday())
    while not target:
        if week_start.year != today_date.year:
            holidays |= us_public_holidays(week_start.year)
        for weekday in priority_days:
            candidate = week_start + timedelta(days=weekday)
            if candidate >= check_from and slot_available(candidate):
                target = candidate
                break
        if not target:
            week_start += timedelta(weeks=1)

# Always 8:00 AM PST = 16:00 UTC — hardcoded regardless of machine timezone.
schedule_datetime = f"{target.isoformat()}T16:00:00"

post_data = json.dumps({"date_gmt": schedule_datetime, "status": "future"}).encode()
req = urllib.request.Request(
    f"{WP_BASE}/posts/{POST_ID}",
    data=post_data,
    headers={**headers, "Content-Type": "application/json"},
    method="POST",
)
resp = json.loads(urllib.request.urlopen(req, timeout=30).read())

result = {
    "post_id": POST_ID,
    "scheduled_date": target.isoformat(),
    "scheduled_display": target.strftime("%A, %B %d, %Y"),
    "edit_link": f"https://blog.postman.com/wp-admin/post.php?post={POST_ID}&action=edit",
    "status": resp.get("status"),
}
print(json.dumps(result, indent=2))
with open("/tmp/wp-autoschedule-result.json", "w") as f:
    json.dump(result, f)
