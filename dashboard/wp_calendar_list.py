import os, json, base64, urllib.request
from datetime import datetime, timedelta, timezone, date

WP_BASE = "https://blog.postman.com/wp-json/wp/v2"
username = os.environ.get("WP_USERNAME", "")
app_password = os.environ.get("WP_APP_PASSWORD", "")

if not username or not app_password:
    print("MISSING_CREDS")
    raise SystemExit(0)

auth_str = username + ":" + app_password
auth = base64.b64encode(auth_str.encode()).decode()
headers = {
    "Authorization": "Basic " + auth,
    "User-Agent": "PostmanDevRelDashboard/1.0",
}

PST = timezone(timedelta(hours=-8))
today = datetime.now(PST)


def wp_get(path):
    req = urllib.request.Request(WP_BASE + "/" + path, headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


# Fetch scheduled posts (next 8 weeks)
after = today.strftime("%Y-%m-%dT00:00:00")
until = (today + timedelta(weeks=8)).strftime("%Y-%m-%dT23:59:59")
scheduled = wp_get(
    "posts?status=future&after=" + after + "&before=" + until
    + "&per_page=100&orderby=date&order=asc&_embed=author"
)

# Fetch recently published posts (past 6 months)
six_months_ago = (today - timedelta(days=180)).strftime("%Y-%m-%dT00:00:00")
published = wp_get(
    "posts?status=publish&after=" + six_months_ago
    + "&per_page=100&orderby=date&order=desc&_embed=author"
)

# Fetch recent drafts (past 3 weeks)
three_weeks_ago = (today - timedelta(weeks=3)).strftime("%Y-%m-%dT00:00:00")
drafts = wp_get(
    "posts?status=draft&after=" + three_weeks_ago
    + "&per_page=100&orderby=modified&order=desc&_embed=author"
)


def get_author_name(p):
    embedded_author = p.get("_embedded", {}).get("author", [])
    if embedded_author:
        return embedded_author[0].get("name", "Unknown")
    return "Unknown"

# Build calendar data
calendar_data = {"updated_at": today.isoformat(), "scheduled": [], "published": [], "drafts": []}

for p in scheduled:
    entry = {
        "id": p["id"],
        "title": p["title"]["rendered"],
        "date": p["date"],
        "status": "future",
        "link": p.get("link", ""),
        "edit_link": "https://blog.postman.com/wp-admin/post.php?post=" + str(p["id"]) + "&action=edit",
        "author": get_author_name(p),
    }
    calendar_data["scheduled"].append(entry)

for p in published:
    entry = {
        "id": p["id"],
        "title": p["title"]["rendered"],
        "date": p["date"],
        "status": "publish",
        "link": p.get("link", ""),
        "edit_link": "https://blog.postman.com/wp-admin/post.php?post=" + str(p["id"]) + "&action=edit",
        "author": get_author_name(p),
    }
    calendar_data["published"].append(entry)

for p in drafts:
    entry = {
        "id": p["id"],
        "title": p["title"]["rendered"],
        "modified": p["modified"],
        "status": "draft",
        "link": p.get("link", ""),
        "edit_link": "https://blog.postman.com/wp-admin/post.php?post=" + str(p["id"]) + "&action=edit",
        "author": get_author_name(p),
    }
    calendar_data["drafts"].append(entry)

# Write wp-calendar.json
script_dir = os.path.dirname(os.path.abspath(__file__))
calendar_path = os.path.join(script_dir, "wp-calendar.json")
with open(calendar_path, "w") as f:
    json.dump(calendar_data, f, indent=2)

print(
    "Dashboard calendar updated: "
    + str(len(calendar_data["scheduled"])) + " scheduled, "
    + str(len(calendar_data["published"])) + " published, "
    + str(len(calendar_data["drafts"])) + " drafts"
)

# Output structured data
output = {"scheduled": [], "published": [], "drafts": []}
for p in scheduled:
    output["scheduled"].append({"id": p["id"], "date": p["date"], "title": p["title"]["rendered"], "author": get_author_name(p)})
for p in published:
    output["published"].append({"id": p["id"], "date": p["date"], "title": p["title"]["rendered"], "author": get_author_name(p)})
for p in drafts:
    output["drafts"].append({"id": p["id"], "modified": p["modified"], "title": p["title"]["rendered"], "author": get_author_name(p)})

print("DATA_JSON:" + json.dumps(output))
