---
name: blog-wordpress-stats
description: "Show the number of blog posts published on blog.postman.com between two dates. Prompts for a start and end date, then queries WordPress and displays the count with a post listing."
argument-hint: "[YYYY-MM-DD YYYY-MM-DD] (e.g. '2026-01-01 2026-03-31')"
---

# WordPress Blog Stats — blog.postman.com

Show how many blog posts were published between two dates on the Postman blog.

## Input Handling

This skill prompts the user for a date range:

- **Start date** — the beginning of the range (inclusive), format `YYYY-MM-DD`
- **End date** — the end of the range (inclusive), format `YYYY-MM-DD`

If both dates are provided as arguments (e.g. `/blog-wordpress-stats 2026-01-01 2026-03-31`), use them directly without prompting.

If no arguments are provided, prompt the user:

> What date range would you like stats for?
> - **Start date** (YYYY-MM-DD):
> - **End date** (YYYY-MM-DD):

Validate that:
- Both dates are valid dates in `YYYY-MM-DD` format
- Start date is not after end date
- Neither date is in the future (beyond today)

If validation fails, tell the user what's wrong and ask again.

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

## Step 1: Fetch Published Posts in the Date Range

Write and run a Python script to fetch all published posts between the start and end dates. Handle pagination — if any request returns 100 results, fetch additional pages.

```python
import os, json, base64, urllib.request
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

START_DATE = "YYYY-MM-DD"  # Replace with actual start date
END_DATE = "YYYY-MM-DD"    # Replace with actual end date

after = f"{START_DATE}T00:00:00"
before = f"{END_DATE}T23:59:59"

all_posts = []
page = 1
while True:
    url = f"{WP_BASE}/posts?status=publish&after={after}&before={before}&per_page=100&page={page}&orderby=date&order=asc"
    req = urllib.request.Request(url, headers=headers)
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    all_posts.extend(resp)
    if len(resp) < 100:
        break
    page += 1

# Output as JSON for parsing
print(json.dumps([{
    "id": p["id"],
    "title": p["title"]["rendered"],
    "date": p["date"],
    "link": p["link"],
} for p in all_posts], indent=2))
```

## Step 2: Display Results

Present the results in this format. All dates in PST:

```
Blog Stats — blog.postman.com
{start_date} to {end_date}

Total posts published: 14

  Date             Day   Title
  --------------   ---   ------------------------------------------
  Jan 07, 2026     Wed   "What's New in Postman v11"
  Jan 09, 2026     Thu   "GraphQL Testing with Postman"
  Jan 14, 2026     Tue   "API Security Best Practices for 2026"
  ...

Posts per month:
  January    — 4
  February   — 3
  March      — 7
  ─────────────────
  Total      — 14
```

**Formatting rules:**
- Show the total count prominently at the top
- List every post with its date, day of week, and title
- Include a per-month breakdown at the bottom
- If the range spans a single month, skip the per-month breakdown
- If zero posts were found, say "No posts were published in this date range."

## Error Handling

- **Authentication failure (401/403):** Tell the user their credentials may be invalid or expired. Suggest regenerating the application password.
- **Network timeout:** Retry once. If it fails again, show the error and suggest the user check their network connection or VPN.
- **Invalid date format:** Show the expected format (`YYYY-MM-DD`) and ask again.
