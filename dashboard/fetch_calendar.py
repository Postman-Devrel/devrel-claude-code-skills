import os, json, base64, urllib.request, urllib.parse
from datetime import datetime, timedelta, timezone, date

# Check credentials
username = os.environ.get("WP_USERNAME")
app_password = os.environ.get("WP_APP_PASSWORD")

if not username or not app_password:
    print("CREDENTIALS_MISSING")
    raise SystemExit(0)

WP_BASE = "https://blog.postman.com/wp-json/wp/v2"
auth = base64.b64encode((username + ":" + app_password).encode()).decode()
headers = {
    "Authorization": "Basic " + auth,
    "User-Agent": "PostmanDevRelDashboard/1.0",
}

PST = timezone(timedelta(hours=-8))

def wp_get(path):
    req = urllib.request.Request(WP_BASE + "/" + path, headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

today = datetime.now(PST)

# Step 1: Fetch scheduled posts (next 8 weeks)
after = today.strftime("%Y-%m-%dT00:00:00")
until = (today + timedelta(weeks=8)).strftime("%Y-%m-%dT23:59:59")
url = "posts?status=future&after=" + after + "&before=" + until + "&per_page=100&orderby=date&order=asc"
try:
    scheduled = wp_get(url)
except urllib.error.HTTPError as e:
    if e.code in (401, 403):
        print("AUTH_FAILED: WordPress returned " + str(e.code) + ". Check your WP_USERNAME and WP_APP_PASSWORD.")
        raise SystemExit(1)
    raise

# Step 2: Fetch recently published posts (past 6 months)
six_months_ago = (today - timedelta(days=180)).strftime("%Y-%m-%dT00:00:00")
url = "posts?status=publish&after=" + six_months_ago + "&per_page=100&orderby=date&order=desc"
published = wp_get(url)

# Step 2b: Fetch recent draft posts (past 3 weeks)
three_weeks_ago = (today - timedelta(weeks=3)).strftime("%Y-%m-%dT00:00:00")
url = "posts?status=draft&after=" + three_weeks_ago + "&per_page=100&orderby=modified&order=desc"
drafts = wp_get(url)

# Step 3: Write dashboard calendar file
calendar_data = {
    "updated_at": today.isoformat(),
    "scheduled": [],
    "published": [],
    "drafts": [],
}

for p in scheduled:
    calendar_data["scheduled"].append({
        "id": p["id"],
        "title": p["title"]["rendered"],
        "date": p["date"],
        "status": "future",
        "link": p.get("link", ""),
        "edit_link": "https://blog.postman.com/wp-admin/post.php?post=" + str(p["id"]) + "&action=edit",
    })

for p in published:
    calendar_data["published"].append({
        "id": p["id"],
        "title": p["title"]["rendered"],
        "date": p["date"],
        "status": "publish",
        "link": p.get("link", ""),
        "edit_link": "https://blog.postman.com/wp-admin/post.php?post=" + str(p["id"]) + "&action=edit",
    })

for p in drafts:
    calendar_data["drafts"].append({
        "id": p["id"],
        "title": p["title"]["rendered"],
        "modified": p["modified"],
        "status": "draft",
        "link": p.get("link", ""),
        "edit_link": "https://blog.postman.com/wp-admin/post.php?post=" + str(p["id"]) + "&action=edit",
    })

calendar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wp-calendar.json")
os.makedirs(os.path.dirname(calendar_path), exist_ok=True)
with open(calendar_path, "w") as f:
    json.dump(calendar_data, f, indent=2)

sc = len(calendar_data["scheduled"])
pc = len(calendar_data["published"])
dc = len(calendar_data["drafts"])
print("Dashboard calendar updated: " + str(sc) + " scheduled, " + str(pc) + " published, " + str(dc) + " drafts")

# Step 4: Display results
print("")
print("=" * 80)
print("Editorial Calendar -- blog.postman.com")
print("=" * 80)

# Scheduled posts
print("")
print("Upcoming Scheduled Posts:")
if scheduled:
    print("  " + "ID".ljust(10) + "Date".ljust(35) + "Title")
    print("  " + "-----".ljust(10) + "---------------------------".ljust(35) + "------------------------------------------")
    for p in scheduled:
        dt = datetime.fromisoformat(p["date"]).replace(tzinfo=PST)
        date_str = dt.strftime("%a, %b %d, %Y %I:%M %p") + " PST"
        title = p["title"]["rendered"]
        print("  " + str(p["id"]).ljust(10) + date_str.ljust(35) + '"' + title + '"')
else:
    print("  (none)")

# Published posts
print("")
print("Recently Published (past 6 months):")
if published:
    print("  " + "ID".ljust(10) + "Date".ljust(35) + "Title")
    print("  " + "-----".ljust(10) + "---------------------------".ljust(35) + "------------------------------------------")
    for p in published:
        dt = datetime.fromisoformat(p["date"]).replace(tzinfo=PST)
        date_str = dt.strftime("%a, %b %d, %Y %I:%M %p") + " PST"
        title = p["title"]["rendered"]
        print("  " + str(p["id"]).ljust(10) + date_str.ljust(35) + '"' + title + '"')
else:
    print("  (none)")

# Draft posts
print("")
print("Recent Drafts (past 3 weeks):")
if drafts:
    print("  " + "ID".ljust(10) + "Last Modified".ljust(35) + "Title")
    print("  " + "-----".ljust(10) + "---------------------------".ljust(35) + "------------------------------------------")
    for p in drafts:
        dt = datetime.fromisoformat(p["modified"]).replace(tzinfo=PST)
        date_str = dt.strftime("%a, %b %d, %Y %I:%M %p") + " PST"
        title = p["title"]["rendered"]
        print("  " + str(p["id"]).ljust(10) + date_str.ljust(35) + '"' + title + '"')
else:
    print("  (none)")

# US Public Holidays
def us_public_holidays(year):
    hols = set()
    for month, day in [(1,1), (6,19), (7,4), (11,11), (12,25)]:
        hols.add(date(year, month, day).isoformat())
    def nth_weekday(y, m, weekday, n):
        first = date(y, m, 1)
        offset = (weekday - first.weekday()) % 7
        return date(y, m, 1 + offset + 7 * (n - 1))
    def last_weekday(y, m, weekday):
        if m == 12:
            last_day = date(y + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(y, m + 1, 1) - timedelta(days=1)
        offset = (last_day.weekday() - weekday) % 7
        return last_day - timedelta(days=offset)
    hols.add(nth_weekday(year, 1, 0, 3).isoformat())
    hols.add(nth_weekday(year, 2, 0, 3).isoformat())
    hols.add(last_weekday(year, 5, 0).isoformat())
    hols.add(nth_weekday(year, 9, 0, 1).isoformat())
    hols.add(nth_weekday(year, 10, 0, 2).isoformat())
    hols.add(nth_weekday(year, 11, 3, 4).isoformat())
    return hols

# Next open slots
print("")
print("Next open slots (Mon-Thu, no holidays):")

today_date = today.date()
holidays = us_public_holidays(today_date.year)
two_weeks_out = today_date + timedelta(weeks=2)
if two_weeks_out.year != today_date.year:
    holidays |= us_public_holidays(two_weeks_out.year)

scheduled_dates = set()
for p in scheduled:
    scheduled_dates.add(p["date"][:10])

def slot_available(candidate):
    cand_str = candidate.isoformat()
    if cand_str in holidays:
        return False
    if cand_str in scheduled_dates:
        return False
    return True

open_slots = []
earliest = today_date + timedelta(days=1)

# Step 1: Look for Tue/Thu in next 2 weeks
candidate = earliest
tue_thu_slots = []
while candidate <= two_weeks_out:
    if candidate.weekday() in (1, 3) and slot_available(candidate):
        tue_thu_slots.append(candidate)
    candidate += timedelta(days=1)

if tue_thu_slots:
    open_slots = tue_thu_slots[:3]
else:
    # Step 2: Open Mon/Wed within 2 weeks
    candidate = earliest
    while candidate <= two_weeks_out and len(open_slots) < 3:
        if candidate.weekday() in (0, 2) and slot_available(candidate):
            open_slots.append(candidate)
        candidate += timedelta(days=1)

# Step 3: Search beyond if needed
if len(open_slots) < 3:
    priority_days = [1, 3, 2, 0]
    check_from = two_weeks_out + timedelta(days=1)
    week_start = check_from - timedelta(days=check_from.weekday())
    while len(open_slots) < 3:
        if week_start.year != today_date.year:
            holidays |= us_public_holidays(week_start.year)
        for weekday in priority_days:
            cand = week_start + timedelta(days=weekday)
            if cand < check_from or cand in open_slots:
                continue
            if slot_available(cand):
                open_slots.append(cand)
                if len(open_slots) >= 3:
                    break
        week_start += timedelta(weeks=1)

for i, slot in enumerate(open_slots[:3], 1):
    print("  " + str(i) + ". " + slot.strftime("%A, %B %d, %Y"))
