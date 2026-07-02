#!/usr/bin/env python3
"""Create or update a WordPress draft post. Reads HTML from /tmp/wp-post-content.html."""
import os, json, base64, urllib.request

WP_BASE = "https://blog.postman.com/wp-json/wp/v2"
username = os.environ["WP_USERNAME"]
app_password = os.environ["WP_APP_PASSWORD"]
auth = base64.b64encode(f"{username}:{app_password}".encode()).decode()

# CRITICAL: Read HTML from temp file — never embed HTML inline
with open("/tmp/wp-post-content.html", "r") as f:
    html_content = f.read()

image_results = {}
if os.path.exists("/tmp/wp-image-results.json"):
    with open("/tmp/wp-image-results.json", "r") as f:
        image_results = json.load(f)

meta_description = "META_DESCRIPTION_HERE"  # From Step 1

post_data = {
    "title": "POST_TITLE",
    "content": html_content,
    "status": "draft",
    "excerpt": meta_description,
    "tags": [],       # Replace with tag_ids from Step 5
    "meta": {
        "_yoast_wpseo_metadesc": meta_description,
        "_yoast_wpseo_focuskw": "FOCUS_KEYPHRASE_HERE",
    },
}

TAG_IDS = []  # Replace with actual tag IDs from Step 5
if TAG_IDS:
    post_data["tags"] = TAG_IDS

featured_media_id = image_results.get("featured_media_id")
if featured_media_id:
    post_data["featured_media"] = featured_media_id

POST_ID = None  # Replace with existing post ID or None
if POST_ID:
    url = f"{WP_BASE}/posts/{POST_ID}"
    method = "PUT"
else:
    url = f"{WP_BASE}/posts"
    method = "POST"

req = urllib.request.Request(
    url,
    data=json.dumps(post_data).encode(),
    headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
    method=method,
)

resp = json.loads(urllib.request.urlopen(req, timeout=60).read())
print(json.dumps({
    "id": resp["id"],
    "title": resp["title"]["rendered"],
    "status": resp["status"],
    "link": resp["link"],
    "edit_link": f"https://blog.postman.com/wp-admin/post.php?post={resp['id']}&action=edit"
}, indent=2))
