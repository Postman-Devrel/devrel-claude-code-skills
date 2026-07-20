---
name: blog-wordpress-scheduler
description: "Manage the blog.postman.com editorial calendar — list, reschedule, view monthly counts, or get a YTD summary. Enforces Tue/Thu-first scheduling with no conflicts or US public holidays."
argument-hint: "[list | reschedule | monthly | summary] (e.g. 'list', 'reschedule 12345 2026-04-21', 'reschedule 12345 next', 'monthly', 'summary')"
allowed-tools: ["Bash", "Read", "Write"]
---

# WordPress Blog Scheduler — blog.postman.com

Manage the editorial calendar for the Postman blog. View scheduled and recently published posts, reschedule posts, get monthly post counts, and view a YTD summary — all times in PST.

## Input Handling

This skill accepts a subcommand as its argument:

- **`list`** (default if no argument) — Show upcoming scheduled posts and recently published posts from the past 2 weeks
- **`reschedule <post_id> <YYYY-MM-DD | next>`** — Change the scheduled date for a draft or future post. Use a specific date or `next` to automatically pick the next available open slot (Mon-Thu, no holidays, no conflicts)
- **`monthly`** — Show a summary of post counts per month for the current year
- **`summary`** — Show a compact YTD grid with Published, Draft, Scheduled, and Total counts per month

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

Read `references/wp-shared-setup.py` at the start of every script. It provides `WP_BASE`, `headers`, `PST`, `wp_get()`, and `us_public_holidays()`.

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

The `us_public_holidays(year)` function is in `references/wp-shared-setup.py`.

## Subcommand: `list`

### Step 1: Fetch Scheduled Posts

Fetch all posts with `status=future` for the next 8 weeks:

```python
today = datetime.now(PST)
after = today.strftime("%Y-%m-%dT00:00:00")
until = (today + timedelta(weeks=8)).strftime("%Y-%m-%dT23:59:59")

url = f"posts?status=future&after={after}&before={until}&per_page=100&orderby=date&order=asc&_embed=author"
scheduled = wp_get(url)
```

### Step 2: Fetch Recently Published Posts

Fetch posts published in the past 6 months:

```python
six_months_ago = (today - timedelta(days=180)).strftime("%Y-%m-%dT00:00:00")
url = f"posts?status=publish&after={six_months_ago}&per_page=100&orderby=date&order=desc&_embed=author"
published = wp_get(url)
```

### Step 2b: Fetch Recent Draft Posts

Fetch draft posts modified in the past 3 weeks:

```python
three_weeks_ago = (today - timedelta(weeks=3)).strftime("%Y-%m-%dT00:00:00")
url = f"posts?status=draft&after={three_weeks_ago}&per_page=100&orderby=modified&order=desc&_embed=author"
drafts = wp_get(url)
```

### Step 3: Write Dashboard Calendar File

Read `references/wp-write-calendar.py` and run its logic inline (it expects `today`, `scheduled`, `published`, and `drafts` already in scope from Steps 1–2b). This writes `dashboard/wp-calendar.json` for the Kanban UI.

**IMPORTANT:** Always run this step when executing the `list` subcommand. The dashboard reads it on page load.

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

Always include the 3 next available open slots. Use this priority rule:

1. **First**, scan all Tuesday and Thursday dates in the next 2 weeks (starting tomorrow). Collect any that are available (not a holiday, no conflict).
2. **If any Tue/Thu slots are available** in that 2-week window → list only from those, earliest first.
3. **If all Tue/Thu in the next 2 weeks are booked or holidays** → open Mon/Wed within the 2-week window and list from Mon–Thu using priority order [Tue, Thu, Wed, Mon].
4. **If still nothing in the 2-week window** → search beyond 2 weeks using normal priority order [Tue, Thu, Wed, Mon].

Never list a slot on a US holiday or a day with an existing scheduled post.

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

If `date_arg` is `"next"`, read `references/wp-find-slot.py` and run its logic inline — it expects `today_date`, `POST_ID`, `EMBARGO_DATE`, `wp_get`, and `us_public_holidays` in scope, and resolves `target` to the next available date.

If `date_arg` is a specific `YYYY-MM-DD`, parse it directly: `target = date.fromisoformat(date_arg)`.

Then validate `target` against these rules (fail fast and suggest next 3 open slots if any rule fails):

- **Rule 0:** Must not be before `EMBARGO_DATE` (if set)
- **Rule 1:** Must be Mon–Thu (`weekday() <= 3`)
- **Rule 1b:** Mon/Wed only allowed if all Tue/Thu in the next 2 weeks are booked
- **Rule 2:** Must not be a US public holiday (`us_public_holidays(target.year)`)
- **Rule 3:** No existing scheduled post on the same day (exclude the post being rescheduled)
- **Rule 4:** Must not be in the past

If validation fails, show the errors and suggest the next 3 available open slots.

### Step 2: Reschedule the Post

If validation passes, update the post's date to the target date at 8:00 AM PST (which is 16:00 UTC):

```python
# Always 8:00 AM PST = 16:00 UTC — hardcoded regardless of system timezone or user location.
# Use date_gmt (UTC), NOT date (site local time). Sending T16:00:00 to date_gmt = 8am PST.
schedule_datetime = f"{target_str}T16:00:00"

post_data = json.dumps({
    "date_gmt": schedule_datetime,
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

## Subcommand: `summary`

A compact YTD overview grid showing Published, Draft, Scheduled, and Total counts per month. Only months up to and including the current month are shown.

### Step 1: Fetch Posts for the Current Year

Fetch published, scheduled, and draft posts for the current year:

```python
year = datetime.now(PST).year
current_month = datetime.now(PST).month

# Published posts
pub_url = f"posts?status=publish&after={year}-01-01T00:00:00&before={year}-12-31T23:59:59&per_page=100&orderby=date&order=asc"
published = wp_get(pub_url)

# Scheduled (future) posts
sched_url = f"posts?status=future&after={year}-01-01T00:00:00&before={year}-12-31T23:59:59&per_page=100&orderby=date&order=asc"
scheduled = wp_get(sched_url)

# Draft posts (use modified date to catch drafts worked on this year)
draft_url = f"posts?status=draft&after={year}-01-01T00:00:00&per_page=100&orderby=modified&order=desc"
drafts = wp_get(draft_url)
```

Handle pagination — if any query returns exactly 100 results, fetch additional pages until all posts are retrieved.

### Step 2: Group by Month

```python
from collections import defaultdict
import calendar

monthly = defaultdict(lambda: {"published": 0, "draft": 0, "scheduled": 0})

for post in published:
    month_num = int(post["date"][5:7])
    monthly[month_num]["published"] += 1

for post in scheduled:
    month_num = int(post["date"][5:7])
    monthly[month_num]["scheduled"] += 1

for post in drafts:
    month_num = int(post["modified"][5:7])
    monthly[month_num]["draft"] += 1
```

### Step 3: Display the Grid

Present the results as a fixed-width grid. Only show months up to and including the current month. Include a YTD Total row at the bottom.

```
Blog Summary — 2026

  Month        Published   Draft   Scheduled   Total
  -----------  ---------   -----   ---------   -----
  January            8       0         0          8
  February           2       1         0          3
  March              7       0         0          7
  April             13       2         0         15
  May                0       3         1          4
  -----------  ---------   -----   ---------   -----
  YTD Total         30       6         1         37
```

**Formatting rules:**
- Right-align all numeric columns
- Use consistent column widths so the grid stays aligned
- Only show months January through the current month (do not show future months with zero counts)
- The Total column is the sum of Published + Draft + Scheduled for that month
- The YTD Total row sums each column

## Error Handling

- **Authentication failure (401/403):** Tell the user their credentials may be invalid or expired. Suggest regenerating the application password.
- **Post not found (404) on reschedule:** Tell the user the post ID was not found. Suggest running `list` to see valid post IDs.
- **Network timeout:** Retry once. If it fails again, show the error and suggest the user check their network connection or VPN.
- **Invalid date format:** If the user provides a date that cannot be parsed, show the expected format (`YYYY-MM-DD`) and suggest the next 3 open slots.

## Important Guidelines

- **All times use PST (Pacific Standard Time, UTC-8)** — always display and calculate in PST regardless of the system's local timezone.
- **Never allow scheduling on Friday, Saturday, or Sunday** — only Monday through Thursday.
- **Tuesday and Thursday are the primary publishing days** — always fill Tue/Thu slots in the next 2 weeks before offering Mon/Wed. Only suggest or accept Mon/Wed when all Tue and Thu slots in the next 2 weeks are already booked.
- **Never allow scheduling on a US public holiday** — check the holiday list for the target year.
- **Never allow two posts on the same day** — always check for conflicts before rescheduling.
- **Rescheduling sets the time to 8:00 AM PST (16:00 UTC)** — always use the `date_gmt` field with value `T16:00:00`. Never use the `date` field (site local time) and never adjust the time based on the user's system timezone or location. This is hardcoded and must not vary regardless of where the user is running the skill.
- **Do not publish posts directly** — rescheduling sets the status to `future`, not `publish`. The post goes live automatically at the scheduled time.
- **Pagination** — if there are more than 100 posts in a query, make multiple paginated requests to get them all.
