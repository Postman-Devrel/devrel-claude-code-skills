#!/usr/bin/env python3
"""Check for an existing WordPress post by exact title match."""
import os, json, base64, urllib.request, urllib.parse, html

WP_BASE = "https://blog.postman.com/wp-json/wp/v2"
username = os.environ["WP_USERNAME"]
app_password = os.environ["WP_APP_PASSWORD"]
auth = base64.b64encode(f"{username}:{app_password}".encode()).decode()

post_title = "POST_TITLE_HERE"  # Replace with actual title
search_query = urllib.parse.quote(post_title)
url = f"{WP_BASE}/posts?search={search_query}&status=draft,pending,future,publish&per_page=10"

req = urllib.request.Request(url, headers={"Authorization": f"Basic {auth}"})
resp = json.loads(urllib.request.urlopen(req, timeout=30).read())

exact_match = None
for post in resp:
    wp_title = html.unescape(post["title"]["rendered"]).strip()
    if wp_title.lower() == post_title.strip().lower():
        exact_match = post
        print(json.dumps({"id": post["id"], "title": wp_title, "status": post["status"], "link": post["link"]}))
        break

if not exact_match:
    print("No exact title match found — will create a new post.")
