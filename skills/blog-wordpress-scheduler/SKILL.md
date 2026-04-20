---
name: blog-wordpress-scheduler
description: "Manage the blog.postman.com editorial calendar. List scheduled and recently published posts, reschedule drafts/future posts, and view monthly post counts. Enforces Mon-Thu scheduling with no same-day conflicts or US public holidays."
argument-hint: "[list | reschedule | monthly] (e.g. 'list', 'reschedule 12345 2026-04-21', 'reschedule 12345 next', 'monthly')"
---

# WordPress Blog Scheduler — blog.postman.com

Manage the editorial calendar for the Postman blog. View scheduled and recently published posts, reschedule posts, and get monthly post counts — all times in PST.

## Input Handling

This skill accepts a subcommand as its argument:

- **`list`** (default if no argument) — Show upcoming scheduled posts and recently published posts from the past 2 weeks
- **`reschedule <post_id> <YYYY-MM-DD | next>`** — Change the scheduled date for a draft or future post. Use a specific date or `next` to automatically pick the next available open slot (Mon-Thu, no holidays, no conflicts)
- **`monthly`** — Show a summary of post counts per month for the current year

If no argument is provided, default to `list`.

## Prerequisites

This skill requires WordPress credentials. The following environment variables must be set in `~/.claude/settings.json` under `"env"`:

- `WP_USERNAME` — WordPress username for blog.postman.com
- `WP_APP_PASSWORD` — WordPress application password (generate one at blog.postman.com/wp-admin/profile.php under "Application Passwords")

If either is missing, tell the user:
> To use this skill, you need WordPress application credentials. Go to **blog.postman.com/wp-admin/profile.php**, scroll to "Application Passwords", create one, and add these to your `~/.claude/settings.json`:
> ```json
> "env": {
>   "WP_USERNAME": "your-username",
>   "WP_APP_PASSWORD": "xxxx xxxx xxxx xxxx xxxx xxxx"
> }
> ```

## Shared Setup — Authentication & PST Timezone

All Python scripts in this skill should start with this common setup:

```python
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

# All schedule times use PST (UTC-8)
PST = timezone(timedelta(hours=-8))

def wp_get(path):
    req = urllib.request.Request(f"{WP_BASE}/{path}", headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())
```

## US Public Holidays

The following US public holidays must be blocked from scheduling. Before scheduling or suggesting a date, check against this list for the current year. Resolve floating holidays (e.g., "third Monday in January") to their actual dates.

| Holiday | Date |
|---------|------|
| New Year's Day | January 1 |
| Martin Luther King Jr. Day | Third Monday in January |
| Presidents' Day | Third Monday in February |
| Memorial Day | Last Monday in May |
| Juneteenth | June 19 |
| Independence Day | July 4 |
| Labor Day | First Monday in September |
| Columbus Day | Second Monday in October |
| Veterans Day | November 11 |
| Thanksgiving | Fourth Thursday in November |
| Christmas Day | December 25 |

Use this Python function to compute holiday dates for a given year:

```python
def us_public_holidays(year):
    """Return a set of date strings (YYYY-MM-DD) for US public holidays in the given year."""
    from datetime import date
    holidays = set()

    # Fixed-date holidays
    for month, day in [(1,1), (6,19), (7,4), (11,11), (12,25)]:
        holidays.add(date(year, month, day).isoformat())

    # Nth weekday helpers
    def nth_weekday(y, m, weekday, n):
        """Find the nth occurrence of weekday (0=Mon) in month m of year y."""
        first = date(y, m, 1)
        offset = (weekday - first.weekday()) % 7
        return date(y, m, 1 + offset + 7 * (n - 1))

    def last_weekday(y, m, weekday):
        """Find the last occurrence of weekday (0=Mon) in month m of year y."""
        if m == 12:
            last_day = date(y + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(y, m + 1, 1) - timedelta(days=1)
        offset = (last_day.weekday() - weekday) % 7
        return last_day - timedelta(days=offset)

    # MLK Day — 3rd Monday in January
    holidays.add(nth_weekday(year, 1, 0, 3).isoformat())
    # Presidents' Day — 3rd Monday in February
    holidays.add(nth_weekday(year, 2, 0, 3).isoformat())
    # Memorial Day — last Monday in May
    holidays.add(last_weekday(year, 5, 0).isoformat())
    # Labor Day — 1st Monday in September
    holidays.add(nth_weekday(year, 9, 0, 1).isoformat())
    # Columbus Day — 2nd Monday in October
    holidays.add(nth_weekday(year, 10, 0, 2).isoformat())
    # Thanksgiving — 4th Thursday in November
    holidays.add(nth_weekday(year, 11, 3, 4).isoformat())

    return holidays
```

## Subcommand: `list`

### Step 1: Fetch Scheduled Posts

Fetch all posts with `status=future` for the next 8 weeks:

```python
today = datetime.now(PST)
after = today.strftime("%Y-%m-%dT00:00:00")
until = (today + timedelta(weeks=8)).strftime("%Y-%m-%dT23:59:59")

url = f"posts?status=future&after={after}&before={until}&per_page=100&orderby=date&order=asc"
scheduled = wp_get(url)
```

### Step 2: Fetch Recently Published Posts

Fetch posts published in the past 6 months:

```python
six_months_ago = (today - timedelta(days=180)).strftime("%Y-%m-%dT00:00:00")
url = f"posts?status=publish&after={six_months_ago}&per_page=100&orderby=date&order=desc"
published = wp_get(url)
```

### Step 2b: Fetch Recent Draft Posts

Fetch draft posts modified in the past 3 weeks:

```python
three_weeks_ago = (today - timedelta(weeks=3)).strftime("%Y-%m-%dT00:00:00")
url = f"posts?status=draft&after={three_weeks_ago}&per_page=100&orderby=modified&order=desc"
drafts = wp_get(url)
```

### Step 3: Write Dashboard Calendar File

After fetching scheduled, published, and draft posts, write the results to `dashboard/wp-calendar.json` so the Kanban dashboard can display them without calling the WordPress API directly. This file is the bridge between the agent and the dashboard UI.

```python
import os

calendar_data = {
    "updated_at": today.isoformat(),
    "scheduled": [
        {
            "id": p["id"],
            "title": p["title"]["rendered"],
            "date": p["date"],
            "status": "future",
            "link": p.get("link", ""),
            "edit_link": f"https://blog.postman.com/wp-admin/post.php?post={p['id']}&action=edit",
        }
        for p in scheduled
    ],
    "published": [
        {
            "id": p["id"],
            "title": p["title"]["rendered"],
            "date": p["date"],
            "status": "publish",
            "link": p.get("link", ""),
            "edit_link": f"https://blog.postman.com/wp-admin/post.php?post={p['id']}&action=edit",
        }
        for p in published
    ],
    "drafts": [
        {
            "id": p["id"],
            "title": p["title"]["rendered"],
            "modified": p["modified"],
            "status": "draft",
            "link": p.get("link", ""),
            "edit_link": f"https://blog.postman.com/wp-admin/post.php?post={p['id']}&action=edit",
        }
        for p in drafts
    ],
}

calendar_path = os.path.join(os.path.dirname(__file__), "..", "..", "dashboard", "wp-calendar.json")
# Also check relative to CLAUDE_PLUGIN_ROOT if available
if os.environ.get("CLAUDE_PLUGIN_ROOT"):
    calendar_path = os.path.join(os.environ["CLAUDE_PLUGIN_ROOT"], "dashboard", "wp-calendar.json")

os.makedirs(os.path.dirname(calendar_path), exist_ok=True)
with open(calendar_path, "w") as f:
    json.dump(calendar_data, f, indent=2)
print(f"Dashboard calendar updated: {len(calendar_data['scheduled'])} scheduled, {len(calendar_data['published'])} published, {len(calendar_data['drafts'])} drafts")
```

**IMPORTANT:** Always write this file when running the `list` subcommand. The dashboard reads it on page load.

### Step 4: Display Results

Present the results in this format. All times in PST:

```
Editorial Calendar — blog.postman.com

Upcoming Scheduled Posts:
  ID      Date                          Title
  -----   ---------------------------   ------------------------------------------
  12345   Tue, Apr 21, 2026 8:00 AM PST   "Testing OAuth 2.0 Flows in Postman"
  12346   Wed, Apr 22, 2026 8:00 AM PST   "API Security Best Practices for 2026"
  12347   Thu, Apr 23, 2026 8:00 AM PST   "Getting Started with Postman Flows"

Recently Published (past 6 months):
  ID      Date                          Title
  -----   ---------------------------   ------------------------------------------
  12340   Thu, Apr 10, 2026 8:00 AM PST   "What's New in Postman v11"
  12338   Tue, Apr 08, 2026 8:00 AM PST   "GraphQL Testing with Postman"

Recent Drafts (past 3 weeks):
  ID      Last Modified                 Title
  -----   ---------------------------   ------------------------------------------
  12350   Sun, Apr 19, 2026 3:45 PM PST   "Introduction to Postman Vault"
  12351   Fri, Apr 17, 2026 11:20 AM PST  "Using Postman with Azure API Management"

Next open slots (Mon-Thu, no holidays):
  1. Monday, April 27, 2026
  2. Tuesday, April 28, 2026
  3. Wednesday, April 29, 2026
```

Always include the 3 next available open slots. **Prioritize Tuesday and Thursday first, then Wednesday and Monday.** For each upcoming week, try to fill Tue and Thu before offering Wed or Mon. Not on a US holiday, not on a day with an existing scheduled post.

## Subcommand: `reschedule <post_id> <YYYY-MM-DD>`

### Step 0: Check for Embargo Date

Before scheduling, ask the user:

> "Is there an embargo date for this post? (Enter a date as YYYY-MM-DD, or press Enter for no embargo)"

If the user provides an embargo date:
- Validate it is a valid future date
- Store it as `embargo_date`
- The post **must not** be scheduled before this date — only consider dates on or after the embargo date
- Tell the user: "Embargo noted — will only schedule on or after {embargo_date}"

If the user presses Enter or says no, proceed without an embargo constraint.

### Step 1: Resolve and Validate the Target Date

If the user passed `next` instead of a date, resolve it to the next available open slot before validating. **If an embargo date was set in Step 0, skip any candidate dates before the embargo date.**

```python
from datetime import date

date_arg = "TARGET_DATE_OR_NEXT"

if date_arg.lower() == "next":
    # Find the next available slot, prioritizing Tue/Thu over Wed/Mon
    # Priority order: Tuesday (1), Thursday (3), Wednesday (2), Monday (0)
    holidays = us_public_holidays(datetime.now(PST).year)
    priority_days = [1, 3, 2, 0]  # Tue, Thu, Wed, Mon

    # EMBARGO_DATE should be set from Step 0 (None if no embargo)
    EMBARGO_DATE = None  # Replace with date object if embargo was provided

    # Start searching from tomorrow, or from the embargo date if later
    earliest = date.today() + timedelta(days=1)
    if EMBARGO_DATE and EMBARGO_DATE > earliest:
        earliest = EMBARGO_DATE

    target = None
    week_start = earliest - timedelta(days=earliest.weekday())  # Round to Monday

    while target is None:
        # Check next year's holidays too if we cross a year boundary
        if week_start.year != datetime.now(PST).year:
            holidays |= us_public_holidays(week_start.year)

        # Try each day in priority order for this week
        for weekday in priority_days:
            candidate = week_start + timedelta(days=weekday)
            if candidate < earliest:
                continue
            cand_str = candidate.isoformat()
            if cand_str in holidays:
                continue
            # Check for existing scheduled posts on this date
            url = f"posts?status=future&after={cand_str}T00:00:00&before={cand_str}T23:59:59&per_page=10"
            existing = wp_get(url)
            conflicts = [p for p in existing if p["id"] != POST_ID]
            if not conflicts:
                target = candidate
                break

        week_start += timedelta(weeks=1)

    target_str = target.isoformat()
    if EMBARGO_DATE:
        print(f"Next available date (after embargo {EMBARGO_DATE}): {target.strftime('%A, %B %d, %Y')}")
    else:
        print(f"Next available date: {target.strftime('%A, %B %d, %Y')}")
else:
    target = date.fromisoformat(date_arg)
target_str = target.isoformat()
holidays = us_public_holidays(target.year)

errors = []

# Rule 0: Must not be before embargo date
if EMBARGO_DATE and target < EMBARGO_DATE:
    errors.append(f"{target_str} is before the embargo date ({EMBARGO_DATE.isoformat()}). Must schedule on or after the embargo.")

# Rule 1: Must be Mon-Thu (weekday 0-3)
if target.weekday() > 3:
    day_name = target.strftime("%A")
    errors.append(f"{target_str} is a {day_name}. Posts can only be scheduled Monday through Thursday.")

# Rule 2: Must not be a US public holiday
if target_str in holidays:
    errors.append(f"{target_str} is a US public holiday. Choose a different date.")

# Rule 3: Must not conflict with another scheduled post
url = f"posts?status=future&after={target_str}T00:00:00&before={target_str}T23:59:59&per_page=10"
existing = wp_get(url)
# Exclude the post being rescheduled from conflict check
conflicts = [p for p in existing if p["id"] != POST_ID]
if conflicts:
    titles = ", ".join(f'"{p["title"]["rendered"]}"' for p in conflicts)
    errors.append(f"{target_str} already has a scheduled post: {titles}. Choose a different date.")

# Rule 4: Must not be in the past
if target <= date.today():
    errors.append(f"{target_str} is in the past. Choose a future date.")

if errors:
    print("Cannot reschedule to this date:")
    for e in errors:
        print(f"  - {e}")
    # Suggest next 3 open slots
    # ... (use the same open-slot logic from the list subcommand)
```

If validation fails, show the errors and suggest the next 3 available open slots.

### Step 2: Reschedule the Post

If validation passes, update the post's date to the target date at 8:00 AM PST (which is 16:00 UTC):

```python
# 8:00 AM PST = 16:00 UTC
schedule_datetime = f"{target_str}T16:00:00"

post_data = json.dumps({
    "date": schedule_datetime,
    "status": "future"
}).encode()

req = urllib.request.Request(
    f"{WP_BASE}/posts/{POST_ID}",
    data=post_data,
    headers={
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
        "User-Agent": "PostmanDevRelDashboard/1.0",
    },
    method="POST",
)
resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
```

### Step 3: Confirm the Change

Show a confirmation:

```
Post rescheduled.

  Post:     "Testing OAuth 2.0 Flows in Postman" (ID: 12345)
  New date: Tuesday, April 21, 2026 at 8:00 AM PST
  Edit:     https://blog.postman.com/wp-admin/post.php?post=12345&action=edit
```

## Subcommand: `monthly`

### Step 1: Fetch Posts for the Current Year

Fetch all published and scheduled posts for the current year:

```python
year = datetime.now(PST).year

# Published posts
pub_url = f"posts?status=publish&after={year}-01-01T00:00:00&before={year}-12-31T23:59:59&per_page=100&orderby=date&order=asc"
published = wp_get(pub_url)

# Scheduled (future) posts
sched_url = f"posts?status=future&after={year}-01-01T00:00:00&before={year}-12-31T23:59:59&per_page=100&orderby=date&order=asc"
scheduled = wp_get(sched_url)

all_posts = published + scheduled
```

### Step 2: Group by Month and Display

```python
from collections import defaultdict

monthly = defaultdict(lambda: {"published": 0, "scheduled": 0, "titles": []})

for post in all_posts:
    month_key = post["date"][:7]  # YYYY-MM
    status = "published" if post["status"] == "publish" else "scheduled"
    monthly[month_key][status] += 1
    monthly[month_key]["titles"].append((post["date"][:10], post["title"]["rendered"], status))
```

Present in this format:

```
Blog Post Summary — 2026

  Month       Published   Scheduled   Total
  ---------   ---------   ---------   -----
  January          4           0         4
  February         3           0         3
  March            5           0         5
  April            2           3         5
  May              0           2         2
  ---------   ---------   ---------   -----
  YTD Total       14           5        19

Current month detail (April 2026):
  Apr 01 (Tue)  Published  "What's New in Postman v11"
  Apr 08 (Tue)  Published  "GraphQL Testing with Postman"
  Apr 15 (Tue)  Scheduled  "Testing OAuth 2.0 Flows in Postman"
  Apr 22 (Wed)  Scheduled  "API Security Best Practices for 2026"
  Apr 23 (Thu)  Scheduled  "Getting Started with Postman Flows"
```

Always include a detail breakdown for the current month showing each post with its date, day, status, and title.

## Error Handling

- **Authentication failure (401/403):** Tell the user their credentials may be invalid or expired. Suggest regenerating the application password.
- **Post not found (404) on reschedule:** Tell the user the post ID was not found. Suggest running `list` to see valid post IDs.
- **Network timeout:** Retry once. If it fails again, show the error and suggest the user check their network connection or VPN.
- **Invalid date format:** If the user provides a date that cannot be parsed, show the expected format (`YYYY-MM-DD`) and suggest the next 3 open slots.

## Important Guidelines

- **All times use PST (Pacific Standard Time, UTC-8)** — always display and calculate in PST regardless of the system's local timezone.
- **Never allow scheduling on Friday, Saturday, or Sunday** — only Monday through Thursday.
- **Never allow scheduling on a US public holiday** — check the holiday list for the target year.
- **Never allow two posts on the same day** — always check for conflicts before rescheduling.
- **Rescheduling sets the time to 8:00 AM PST** — this is the standard publish time for all posts.
- **Do not publish posts directly** — rescheduling sets the status to `future`, not `publish`. The post goes live automatically at the scheduled time.
- **Pagination** — if there are more than 100 posts in a query, make multiple paginated requests to get them all.
