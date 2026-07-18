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
    url = f"{WP_BASE}/posts?status=publish&after={after}&before={before}&per_page=100&page={page}&orderby=date&order=asc&_embed=author"
    req = urllib.request.Request(url, headers=headers)
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    all_posts.extend(resp)
    if len(resp) < 100:
        break
    page += 1

def get_author_name(p):
    embedded_author = p.get("_embedded", {}).get("author", [])
    if embedded_author:
        return embedded_author[0].get("name", "Unknown")
    return "Unknown"

# Output as JSON for parsing
print(json.dumps([{
    "id": p["id"],
    "title": p["title"]["rendered"],
    "date": p["date"],
    "link": p["link"],
    "author": get_author_name(p),
} for p in all_posts], indent=2))
