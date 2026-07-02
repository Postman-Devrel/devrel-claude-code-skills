#!/usr/bin/env python3
"""Convert a Google Doc to blog-ready markdown with local images. Steps 0a-0d."""
import re, os, urllib.request, urllib.parse, subprocess, sys

GOOGLE_DOCS_URL = "GOOGLE_DOCS_URL_HERE"  # Replace with actual URL

# 0a: Extract document ID
match = re.search(r'/document/d/([a-zA-Z0-9_-]+)', GOOGLE_DOCS_URL)
if not match:
    raise ValueError(f"Could not extract document ID from URL: {GOOGLE_DOCS_URL}")
doc_id = match.group(1)
print(f"Document ID: {doc_id}")

# 0b: Fetch HTML and extract title/slug
html_url = f"https://docs.google.com/document/d/{doc_id}/export?format=html"
req = urllib.request.Request(html_url, headers={"User-Agent": "PostmanDevRelSkill/1.0"})
html_content = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

title_match = re.search(r'<title>(.*?)</title>', html_content)
doc_title = title_match.group(1).strip() if title_match else "untitled"
slug = re.sub(r'[^\w\s-]', '', doc_title.lower().strip())
slug = re.sub(r'[\s_]+', '-', slug)
slug = re.sub(r'-+', '-', slug).strip('-')
print(f"Title: {doc_title}  Slug: {slug}")

# 0c: Download embedded images
image_dir = f"blog-output/images/{slug}"
os.makedirs(image_dir, exist_ok=True)

img_pattern = re.compile(r'<img[^>]+src="([^"]+)"', re.IGNORECASE)
img_urls = img_pattern.findall(html_content)

image_map = {}
for i, img_url in enumerate(img_urls, 1):
    try:
        if not img_url.startswith("http"):
            continue
        req = urllib.request.Request(img_url, headers={"User-Agent": "PostmanDevRelSkill/1.0"})
        img_data = urllib.request.urlopen(req, timeout=30).read()
        ext = "jpg" if any(img_url.endswith(e) for e in [".jpg", ".jpeg"]) else "gif" if img_url.endswith(".gif") else "png"
        filename = f"image-{i}.{ext}"
        filepath = os.path.join(image_dir, filename)
        with open(filepath, "wb") as f:
            f.write(img_data)
        image_map[img_url] = f"images/{slug}/{filename}"
        print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Failed to download image {i}: {e}")

# 0d: Convert HTML to markdown and save
subprocess.check_call([sys.executable, "-m", "pip", "install", "html2text", "-q"])
import html2text

h = html2text.HTML2Text()
h.body_width = 0
h.ignore_links = False
h.ignore_images = False
h.unicode_snob = True
h.skip_internal_links = True
markdown = h.handle(html_content)

for old_url, local_path in image_map.items():
    markdown = markdown.replace(old_url, local_path)

google_redirect = re.compile(r'https://www\.google\.com/url\?q=(.*?)&[^)]*')
markdown = google_redirect.sub(lambda m: urllib.parse.unquote(m.group(1)), markdown)
markdown = re.sub(r'\n{3,}', '\n\n', markdown)
markdown = re.sub(r'\[([^\]]*)\]\(#[^)]*\)', r'\1', markdown)

first_para_match = re.search(r'\n\n([^#\n].{20,})', markdown)
meta_desc = ""
if first_para_match:
    meta_desc = first_para_match.group(1).strip()[:155]
    meta_desc = meta_desc[:meta_desc.rfind(' ')] if len(meta_desc) == 155 else meta_desc

frontmatter = f"""---
suggested_title: "{doc_title}"
meta_description: "{meta_desc}"
seo_score: 0
primary_keyword: ""
secondary_keywords: []
source_gdoc: "https://docs.google.com/document/d/{doc_id}/edit"
---

"""

output_path = f"blog-output/{slug}.md"
with open(output_path, "w") as f:
    f.write(frontmatter + markdown)
print(f"Saved: {output_path}")
