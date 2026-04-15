---
name: blog-wordpress-stage
description: "Stage a blog post to WordPress (blog.postman.com). Takes a markdown file and header image, creates or updates a draft post, uploads the featured image, sets the meta description, and suggests the next available publish date (Tue/Wed/Thu)."
argument-hint: "[markdown file path] [header image path] (e.g. 'blog-output/my-post.md blog-output/images/header/header-my-post.png')"
---

# WordPress Blog Post Stager — blog.postman.com

Stage blog posts to the Postman WordPress site. Converts markdown to HTML, uploads a featured image, sets SEO metadata, and finds the next open publish slot on the Tuesday/Wednesday/Thursday schedule.

## Input Handling

This skill accepts:

- **Markdown file path** (required) — path to a blog post markdown file (e.g., `blog-output/testing-oauth-flows.md`)
- **Header image path** (optional) — path to a header image PNG

If no arguments are provided, ask the user for the markdown file path.

**Automatic header image detection:** If only the markdown file is provided, automatically look for a matching header image at `blog-output/images/header/header-{markdown-basename}.png`. For example, if the markdown file is `blog-output/testing-oauth-flows.md`, check for `blog-output/images/header/header-testing-oauth-flows.png`. If found, use it as the featured image without asking. If not found, stage the post without a featured image.

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

## Workflow

### Step 1: Read and Parse the Markdown File

1. Read the markdown file using the Read tool
2. Extract YAML frontmatter fields:
   - `suggested_title` — use as the WordPress post title
   - `meta_description` — use as the Yoast SEO meta description
   - `primary_keyword` — use as the Yoast focus keyphrase
   - `secondary_keywords` — for reference
3. Extract the markdown body (everything after the frontmatter closing `---`)
4. If `meta_description` is missing from frontmatter, generate one from the first two paragraphs of the post (under 155 characters, includes the primary topic and a call to action)

### Step 2: Convert Markdown to HTML

Write and run a Python script to convert the markdown body to HTML suitable for WordPress. **CRITICAL: Save the HTML to a temp file** — do NOT try to embed the HTML inline in the post creation script, as this will break on quotes and special characters.

```python
import subprocess, sys

# Install markdown if needed
subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown", "-q"])

import markdown

with open("INPUT_FILE", "r") as f:
    content = f.read()

# Strip frontmatter
parts = content.split("---", 2)
if len(parts) >= 3:
    body = parts[2].strip()
else:
    body = content.strip()

html = markdown.markdown(body, extensions=["fenced_code", "codehilite", "tables", "toc"])

# Write HTML to temp file for the post creation script to read
with open("/tmp/wp-post-content.html", "w") as f:
    f.write(html)

print(f"HTML saved to /tmp/wp-post-content.html ({len(html)} chars)")
```

The HTML is now at `/tmp/wp-post-content.html` for use in Step 5.

### Step 3: Upload All Images

Upload **all** images referenced in the blog post to WordPress — both the featured header image and any inline images in the markdown body.

#### 3a: Find All Local Images

Scan the HTML content (from Step 2) and the markdown body for local image references. These include:
- Relative paths like `images/{slug}/image-1.png` (from Google Doc imports)
- Paths like `blog-output/images/...`

Also check for the featured header image (auto-detected from `blog-output/images/header/header-{slug}.png` or provided as an argument).

#### 3b: Upload Each Image

For each local image, upload it to WordPress via the Media REST API and record the mapping from local path to WordPress URL.

Write and run a Python script at `/tmp/wp-upload-images.py`:

```python
import os, json, base64, re, urllib.request, mimetypes

WP_BASE = "https://blog.postman.com/wp-json/wp/v2"
username = os.environ["WP_USERNAME"]
app_password = os.environ["WP_APP_PASSWORD"]
auth = base64.b64encode(f"{username}:{app_password}".encode()).decode()
headers_base = {
    "Authorization": f"Basic {auth}",
    "User-Agent": "PostmanDevRelDashboard/1.0",
}

BLOG_OUTPUT = "blog-output"  # Adjust if needed
MARKDOWN_FILE = "INPUT_FILE_HERE"

def upload_image(image_path):
    """Upload a single image to WordPress and return {id, source_url}."""
    filename = os.path.basename(image_path)
    mime_type = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        image_data = f.read()
    req = urllib.request.Request(
        f"{WP_BASE}/media",
        data=image_data,
        headers={
            **headers_base,
            "Content-Type": mime_type,
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
        method="POST",
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=60).read())
    return {"id": resp["id"], "source_url": resp["source_url"]}

# Read the HTML content
with open("/tmp/wp-post-content.html", "r") as f:
    html_content = f.read()

# Find all image src references in the HTML
img_srcs = re.findall(r'<img[^>]+src="([^"]+)"', html_content, re.IGNORECASE)

# Also find markdown image references: ![alt](path)
with open(MARKDOWN_FILE, "r") as f:
    md_content = f.read()
md_imgs = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', md_content)
all_img_refs = set(img_srcs + md_imgs)

# Upload local images and build a replacement map
image_map = {}  # local path → WP URL
featured_media_id = None

for ref in all_img_refs:
    # Skip external URLs
    if ref.startswith("http://") or ref.startswith("https://"):
        continue

    # Resolve the local path relative to blog-output/
    candidates = [
        ref,
        os.path.join(BLOG_OUTPUT, ref),
        os.path.join(os.path.dirname(MARKDOWN_FILE), ref),
    ]
    local_path = None
    for c in candidates:
        if os.path.isfile(c):
            local_path = c
            break

    if not local_path:
        print(f"Skipping (not found): {ref}")
        continue

    try:
        result = upload_image(local_path)
        image_map[ref] = result["source_url"]
        print(f"Uploaded: {ref} → {result['source_url']}")
    except Exception as e:
        print(f"Failed to upload {ref}: {e}")

# Upload the featured header image
HEADER_IMAGE = "HEADER_IMAGE_PATH_OR_NONE"  # Replace with actual path or None
if HEADER_IMAGE and os.path.isfile(HEADER_IMAGE):
    try:
        result = upload_image(HEADER_IMAGE)
        featured_media_id = result["id"]
        print(f"Featured image uploaded: {result['source_url']}")
    except Exception as e:
        print(f"Failed to upload featured image: {e}")

# Replace local paths with WordPress URLs in the HTML
for local_ref, wp_url in image_map.items():
    html_content = html_content.replace(local_ref, wp_url)

# Save the updated HTML
with open("/tmp/wp-post-content.html", "w") as f:
    f.write(html_content)

print(f"\nUploaded {len(image_map)} inline image(s)")
print(f"Featured media ID: {featured_media_id}")
# Save results for Step 6
with open("/tmp/wp-image-results.json", "w") as f:
    json.dump({"image_map": image_map, "featured_media_id": featured_media_id}, f)
```

Save the `featured_media_id` for use in Step 6. The HTML file now has WordPress URLs for all images.

### Step 4: Check for an Existing Post

Before creating a new post, search for an existing post with the same title to avoid duplicates. Only treat a post as a match if the title is **exactly** the same (case-insensitive comparison after stripping HTML entities):

```python
import os, json, base64, urllib.request, urllib.parse, html

WP_BASE = "https://blog.postman.com/wp-json/wp/v2"
username = os.environ["WP_USERNAME"]
app_password = os.environ["WP_APP_PASSWORD"]
auth = base64.b64encode(f"{username}:{app_password}".encode()).decode()

post_title = "POST_TITLE_HERE"
search_query = urllib.parse.quote(post_title)
url = f"{WP_BASE}/posts?search={search_query}&status=draft,pending,future,publish&per_page=10"

req = urllib.request.Request(url, headers={"Authorization": f"Basic {auth}"})
resp = json.loads(urllib.request.urlopen(req, timeout=30).read())

# Only match if the title is exactly the same (WordPress search returns partial matches)
exact_match = None
for post in resp:
    wp_title = html.unescape(post["title"]["rendered"]).strip()
    if wp_title.lower() == post_title.strip().lower():
        exact_match = post
        print(json.dumps({"id": post["id"], "title": wp_title, "status": post["status"], "link": post["link"]}))
        break

if not exact_match:
    print("No exact title match found — will create a new post.")
```

- If an **exact** title match is found, use its `post_id` to **update** the existing post in Step 5
- If no exact match is found (even if partial matches exist), **create** a new post in Step 5
- Tell the user whether you are creating or updating

### Step 5: Generate and Resolve Tags

Analyze the blog post content and choose **3 tags** that best describe the post's topic. Tags should be specific and useful for readers browsing by topic (e.g., "API Testing", "OAuth 2.0", "CI/CD" — not generic ones like "Postman" or "Development").

Use the `primary_keyword` and `secondary_keywords` from the frontmatter as a starting point, but adjust based on the actual content.

For each tag, check if it already exists in WordPress. If it does, use the existing tag ID. If not, create it.

```python
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
    # Search for existing tag
    search_url = f"{WP_BASE}/tags?search={urllib.parse.quote(tag_name)}&per_page=5"
    req = urllib.request.Request(search_url, headers=headers)
    existing = json.loads(urllib.request.urlopen(req, timeout=30).read())

    found = None
    for t in existing:
        if t["name"].lower() == tag_name.lower():
            found = t["id"]
            break

    if found:
        tag_ids.append(found)
    else:
        # Create the tag
        create_req = urllib.request.Request(
            f"{WP_BASE}/tags",
            data=json.dumps({"name": tag_name}).encode(),
            headers=headers,
            method="POST",
        )
        new_tag = json.loads(urllib.request.urlopen(create_req, timeout=30).read())
        tag_ids.append(new_tag["id"])

print(f"Tag IDs: {tag_ids}")
```

Save the `tag_ids` list for use in Step 6.

### Step 6: Create or Update the Post

Write and run a Python script at `/tmp/wp-stage-post.py`. **CRITICAL: Read the HTML content from `/tmp/wp-post-content.html`** — never embed the HTML inline as a string literal, as it will break on quotes, backticks, and special characters.

```python
import os, json, base64, urllib.request

WP_BASE = "https://blog.postman.com/wp-json/wp/v2"
username = os.environ["WP_USERNAME"]
app_password = os.environ["WP_APP_PASSWORD"]
auth = base64.b64encode(f"{username}:{app_password}".encode()).decode()

# Read HTML from temp file — NEVER embed HTML inline
with open("/tmp/wp-post-content.html", "r") as f:
    html_content = f.read()

# Load image upload results from Step 3
import os
image_results = {}
if os.path.exists("/tmp/wp-image-results.json"):
    with open("/tmp/wp-image-results.json", "r") as f:
        image_results = json.load(f)

post_data = {
    "title": "POST_TITLE",
    "content": html_content,
    "status": "draft",
    "tags": [],  # Replace with tag_ids from Step 5
    "meta": {
        "_yoast_wpseo_metadesc": "META_DESCRIPTION_HERE",
        "_yoast_wpseo_focuskw": "FOCUS_KEYPHRASE_HERE",
    },
}

# Add tags from Step 5
TAG_IDS = []  # Replace with actual tag IDs
if TAG_IDS:
    post_data["tags"] = TAG_IDS

# Add featured image from Step 3
featured_media_id = image_results.get("featured_media_id")
if featured_media_id:
    post_data["featured_media"] = featured_media_id

# POST to create, or PUT to update if post_id exists
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
    headers={
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
    },
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
```

### Step 7: Write WordPress Post ID Back to Markdown

After a successful create or update, write the WordPress post ID into the markdown file's YAML frontmatter as `wordpress_id`. This links the local file to the WordPress post for future updates.

- If `wordpress_id` already exists in the frontmatter, update it with the new value
- If it does not exist, add it after the last frontmatter field (before the closing `---`)

Use the Edit tool to add or update the `wordpress_id` field in the frontmatter. For example, if the frontmatter is:

```yaml
---
suggested_title: "Testing OAuth 2.0 Flows in Postman"
meta_description: "Learn how to test OAuth 2.0 authorization flows..."
---
```

It should become:

```yaml
---
suggested_title: "Testing OAuth 2.0 Flows in Postman"
meta_description: "Learn how to test OAuth 2.0 authorization flows..."
wordpress_id: 12345
---
```

Additionally, when checking for existing posts in Step 4, if the markdown file already contains a `wordpress_id` in its frontmatter, use that ID to fetch the post directly instead of searching by title. This is the most reliable way to match a local file to its WordPress post.

### Step 8: Present Results

This skill only saves the post as a **draft**. It does NOT schedule or suggest publish dates — that is the `blog-wordpress-scheduler` skill's job, and scheduling only happens after a human reviews the draft.

Summarize the result to the user:

1. **Post status** — created or updated, with the WordPress post ID
2. **Edit link** — direct link to edit the post in wp-admin: `https://blog.postman.com/wp-admin/post.php?post={id}&action=edit`
3. **Featured image** — whether it was uploaded and attached (include the image URL)
4. **Meta description** — the meta description that was set
5. **Next step** — remind the user to review the draft in wp-admin, then run `blog-wordpress-scheduler` when ready to schedule

Example output format:

```
WordPress post staged as draft.

  Post:           "Testing OAuth 2.0 Flows in Postman" (draft)
  Post ID:        12345
  Edit:           https://blog.postman.com/wp-admin/post.php?post=12345&action=edit
  Featured image: Uploaded (header-testing-oauth-flows.png)
  Meta desc:      "Learn how to test OAuth 2.0 authorization flows..."

Next step: Review the draft in wp-admin, then run /blog-wordpress-scheduler to pick a publish date.
```

## Error Handling

- **Authentication failure (401/403):** Tell the user their credentials may be invalid or expired. Suggest regenerating the application password.
- **Post not found on update (404):** Fall back to creating a new post.
- **Image upload failure:** Stage the post without a featured image and tell the user the image upload failed with the error message. They can upload manually via wp-admin.
- **Network timeout:** Retry once. If it fails again, show the error and suggest the user check their network connection or VPN.
- **Missing Yoast SEO plugin:** If the meta fields are rejected, warn the user that Yoast SEO may not be installed. The post will still be created but without SEO metadata.

## Important Guidelines

- **Always create posts as drafts** — never publish or schedule directly. The user must review the draft first.
- **Never suggest or set publish dates** — that is the `blog-wordpress-scheduler` skill's responsibility, and only after human review.
- **Only modify the markdown source file to write back `wordpress_id`** — do not change any other content in the file.
- **Preserve all formatting** — code blocks, tables, lists, and headings must render correctly in WordPress.
- **Check for duplicates first** — always search for an existing post before creating a new one to avoid duplicate content.
- **Read HTML from temp file** — never embed HTML content inline in the post creation script. Always read from `/tmp/wp-post-content.html`.
