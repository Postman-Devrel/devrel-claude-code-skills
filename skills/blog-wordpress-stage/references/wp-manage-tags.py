#!/usr/bin/env python3
"""Find or create WordPress tags and return their IDs."""
import os, json, base64, urllib.request, urllib.parse

WP_BASE = "https://blog.postman.com/wp-json/wp/v2"
username = os.environ["WP_USERNAME"]
app_password = os.environ["WP_APP_PASSWORD"]
auth = base64.b64encode(f"{username}:{app_password}".encode()).decode()
headers = {
    "Authorization": f"Basic {auth}",
    "Content-Type": "application/json",
    "User-Agent": "PostmanDevRelDashboard/1.0",
}

TAG_NAMES = ["Tag One", "Tag Two", "Tag Three"]  # Replace with your 3 chosen tags

tag_ids = []
for tag_name in TAG_NAMES:
    search_url = f"{WP_BASE}/tags?search={urllib.parse.quote(tag_name)}&per_page=5"
    req = urllib.request.Request(search_url, headers=headers)
    existing = json.loads(urllib.request.urlopen(req, timeout=30).read())

    found = next((t["id"] for t in existing if t["name"].lower() == tag_name.lower()), None)
    if found:
        tag_ids.append(found)
    else:
        create_req = urllib.request.Request(
            f"{WP_BASE}/tags",
            data=json.dumps({"name": tag_name}).encode(),
            headers=headers,
            method="POST",
        )
        new_tag = json.loads(urllib.request.urlopen(create_req, timeout=30).read())
        tag_ids.append(new_tag["id"])

print(f"Tag IDs: {tag_ids}")
