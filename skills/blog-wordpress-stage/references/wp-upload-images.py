#!/usr/bin/env python3
"""Upload all local images from a blog post to WordPress. Saves results to /tmp/wp-image-results.json."""
import os, json, base64, re, urllib.request, mimetypes

WP_BASE = "https://blog.postman.com/wp-json/wp/v2"
username = os.environ["WP_USERNAME"]
app_password = os.environ["WP_APP_PASSWORD"]
auth = base64.b64encode(f"{username}:{app_password}".encode()).decode()
headers_base = {
    "Authorization": f"Basic {auth}",
    "User-Agent": "PostmanDevRelDashboard/1.0",
}

BLOG_OUTPUT = "blog-output"
MARKDOWN_FILE = "INPUT_FILE_HERE"   # Replace with actual markdown path
HEADER_IMAGE = "HEADER_IMAGE_PATH"  # Replace with header image path or "" for none

def upload_image(image_path):
    filename = os.path.basename(image_path)
    mime_type = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        image_data = f.read()
    req = urllib.request.Request(
        f"{WP_BASE}/media",
        data=image_data,
        headers={**headers_base, "Content-Type": mime_type, "Content-Disposition": f'attachment; filename="{filename}"'},
        method="POST",
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=60).read())
    return {"id": resp["id"], "source_url": resp["source_url"]}

with open("/tmp/wp-post-content.html", "r") as f:
    html_content = f.read()

img_srcs = re.findall(r'<img[^>]+src="([^"]+)"', html_content, re.IGNORECASE)
with open(MARKDOWN_FILE, "r") as f:
    md_content = f.read()
md_imgs = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', md_content)
all_img_refs = set(img_srcs + md_imgs)

image_map = {}
featured_media_id = None

for ref in all_img_refs:
    if ref.startswith("http://") or ref.startswith("https://"):
        continue
    candidates = [ref, os.path.join(BLOG_OUTPUT, ref), os.path.join(os.path.dirname(MARKDOWN_FILE), ref)]
    local_path = next((c for c in candidates if os.path.isfile(c)), None)
    if not local_path:
        print(f"Skipping (not found): {ref}")
        continue
    try:
        result = upload_image(local_path)
        image_map[ref] = result["source_url"]
        print(f"Uploaded: {ref} → {result['source_url']}")
    except Exception as e:
        print(f"Failed to upload {ref}: {e}")

if HEADER_IMAGE and os.path.isfile(HEADER_IMAGE):
    try:
        result = upload_image(HEADER_IMAGE)
        featured_media_id = result["id"]
        print(f"Featured image uploaded: {result['source_url']}")
    except Exception as e:
        print(f"Failed to upload featured image: {e}")

for local_ref, wp_url in image_map.items():
    html_content = html_content.replace(local_ref, wp_url)

with open("/tmp/wp-post-content.html", "w") as f:
    f.write(html_content)

print(f"\nUploaded {len(image_map)} inline image(s), featured_media_id={featured_media_id}")
with open("/tmp/wp-image-results.json", "w") as f:
    json.dump({"image_map": image_map, "featured_media_id": featured_media_id}, f)
